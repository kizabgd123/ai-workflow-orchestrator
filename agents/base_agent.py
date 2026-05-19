import os
import asyncio
from google import genai
from typing import Optional, Dict, Any, Union, List
import json
import re
import logging
from core.types import AgentRole, AgentMode, Argument
from core.key_manager import KeyManager
from orchestrator.router import ModelRouter
from core.prompts import SYSTEM_PROMPT_TEMPLATE, ROLE_INSTRUCTIONS, DEBATE_PROMPT_TEMPLATE

logger = logging.getLogger("BaseAgent")


class BaseAgent:
    def __init__(
        self,
        role: AgentRole,
        agent_id: str,
        key_manager: KeyManager,
        model_router: ModelRouter,
    ):
        self.role = role
        self.agent_id = agent_id
        self.key_manager = key_manager
        self.model_router = model_router
        self.mode = AgentMode.EXECUTION
        self.system_prompt = self._get_system_prompt()
        self.memory_buffer: List[Dict[str, Any]] = []

    def _get_genai_model(self):
        key = self.key_manager.get_next_key()
        client = genai.Client(api_key=key)
        return client, key

    def _get_system_prompt(self) -> str:
        """Returns the specialized system prompt based on the agent's role using centralized templates."""
        role_name = self.role.value if hasattr(self.role, 'value') else str(self.role)
        role_instructions = ROLE_INSTRUCTIONS.get(role_name, "Perform your assigned tasks with precision.")
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            role_name=role_name,
            agent_id=self.agent_id,
            role_instructions=role_instructions
        )

    def set_mode(self, mode: AgentMode):
        self.mode = mode

    async def think(
        self, prompt: str, context: Optional[str] = None
    ) -> Union[str, Argument]:
        """Calls Gemini to generate a response with adversarial context awareness."""
        from security.token_budget import TokenBudgetTracker
        tracker = TokenBudgetTracker()

        if tracker.is_tripped():
            logger.error(f"[CIRCUIT BREAKER] Agent {self.agent_id} aborted: Token budget exceeded.")
            raise ValueError(f"Agent {self.agent_id} aborted: Token budget exceeded.")

        max_retries = 3
        for attempt in range(max_retries):
            client, key = self._get_genai_model()
            try:
                if self.mode == AgentMode.DEBATE:
                    user_input = DEBATE_PROMPT_TEMPLATE.format(
                        objective=prompt,
                        context=context or "No previous history.",
                        role=self.role.value,
                    )
                else:
                    user_input = f"Context: {context}\n\nInput: {prompt}" if context else f"Input: {prompt}"

                model_name = self.model_router.get_model(self.role)
                
                # Use system_instruction parameter if supported by the SDK version, 
                # otherwise prepend to contents.
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=user_input,
                    config={
                        "system_instruction": self.system_prompt,
                        "response_mime_type": "application/json" if self.mode == AgentMode.DEBATE else "text/plain"
                    }
                )

                response_text = response.text if response.text is not None else ""
                
                # Proactive token tracking (estimate)
                input_tokens = (len(self.system_prompt) + len(user_input)) // 4
                output_tokens = len(response_text) // 4
                tracker.consume(input_tokens, output_tokens)

                if self.mode == AgentMode.DEBATE:
                    return self._parse_debate_response(response_text)

                return response_text

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for agent {self.agent_id}: {e}")
                if "429" in str(e):
                    self.key_manager.report_failure(key)
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                
                # Fallback for older models or SDK issues: retry without response_mime_type
                if "mime_type" in str(e).lower():
                     response = await client.aio.models.generate_content(
                        model=model_name,
                        contents=f"{self.system_prompt}\n\n{user_input}"
                    )
                     response_text = response.text or ""
                     if self.mode == AgentMode.DEBATE:
                        return self._parse_debate_response(response_text)
                     return response_text
                
                if attempt == max_retries - 1:
                    raise e

        raise Exception("Agent exhausted retries.")

    def _parse_debate_response(self, text: str) -> Argument:
        """Parses the JSON response from the debate round."""
        try:
            # Clean text if it contains markdown code blocks
            clean_text = text
            if "```json" in text:
                clean_text = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL).group(1)
            elif "```" in text:
                clean_text = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL).group(1)

            data = json.loads(clean_text)

            # Map fields to Argument model (supporting multiple naming variants)
            content = data.get("argument") or data.get("content") or text
            confidence = float(data.get("confidence_score") or data.get("confidence") or 0.5)
            is_pro = bool(data.get("is_pro", True))

            return Argument(
                agent_id=self.agent_id,
                role=self.role,
                content=content,
                confidence=confidence,
                is_pro=is_pro, # Note: core/types.py might need update to include is_pro
                round=0,
            )
        except Exception as e:
            logger.error(f"Failed to parse debate JSON from {self.agent_id}: {e}. Raw text: {text[:200]}...")
            return Argument(
                agent_id=self.agent_id,
                role=self.role,
                content=f"Error parsing response: {text[:500]}",
                confidence=0.1,
                round=0,
            )
