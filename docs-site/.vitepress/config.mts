import { defineConfig } from 'vitepress'

export default defineConfig({
  srcDir: '../docs',
  title: 'AI Workflow Orchestrator',
  description: 'Siguran, audita-bilan i otporan višestruki agent sistem sa debatom i memorijom',
  lastUpdated: true,
  cleanUrls: true,

  // Multi-Language Configurations
  locales: {
    root: {
      label: 'Srpski',
      lang: 'sr',
      themeConfig: {
        nav: [
          { text: 'Početna', link: '/' },
          { text: 'Analiza Koda', link: '/analysis' },
          { text: 'Arhitektura', link: '/architecture' },
          { text: 'SOP', link: '/sop/' },
          { text: 'API Referenca', link: '/api/' }
        ],
        sidebar: [
          {
            text: 'Osnovne Analize',
            items: [
              { text: 'Analiza Koda', link: '/analysis' },
              { text: 'Arhitektura Sistema', link: '/architecture' },
              { text: 'Baza Podataka', link: '/database' }
            ]
          },
          {
            text: 'Operativne Tokove',
            items: [
              { text: 'Tokovi Podataka', link: '/data-flow' },
              { text: 'Procesi i Stanja', link: '/flows/' }
            ]
          },
          {
            text: 'Poslovni Model',
            items: [
              { text: 'Persone Korisnika', link: '/personas/' },
              { text: 'JTBD Platno', link: '/jtbd/' }
            ]
          },
          {
            text: 'SOP Operativni Vodiči',
            collapsed: false,
            items: [
              { text: 'SOP Indeks', link: '/sop/' },
              { text: 'SOP-001: Instalacija', link: '/sop/setup' },
              { text: 'SOP-002: Dijagnostika', link: '/sop/troubleshooting' }
            ]
          },
          {
            text: 'API Specifikacije',
            items: [
              { text: 'FastAPI REST API', link: '/api/' }
            ]
          },
          {
            text: 'Uputstvo za Implementaciju',
            items: [
              { text: 'Kontejneri & Deploy', link: '/deployment' }
            ]
          }
        ],
        docFooter: {
          prev: 'Prethodna strana',
          next: 'Sledeća strana'
        },
        outline: {
          label: 'Sadržaj stranice'
        },
        lastUpdated: {
          text: 'Ažurirano'
        }
      }
    },
    en: {
      label: 'English',
      lang: 'en',
      link: '/en/',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Codebase Analysis', link: '/en/analysis' },
          { text: 'Architecture', link: '/en/architecture' },
          { text: 'SOP', link: '/en/sop/' },
          { text: 'API Specs', link: '/en/api/' }
        ],
        sidebar: [
          {
            text: 'Core Audits',
            items: [
              { text: 'Codebase Footprint', link: '/en/analysis' },
              { text: 'System Architecture', link: '/en/architecture' },
              { text: 'Database Design', link: '/en/database' }
            ]
          },
          {
            text: 'Data and Processes',
            items: [
              { text: 'Data Sequence Flows', link: '/en/data-flow' },
              { text: 'FSM State Transitions', link: '/en/flows/' }
            ]
          },
          {
            text: 'Product & Design',
            items: [
              { text: 'Buyer & User Personas', link: '/en/personas/' },
              { text: 'JTBD Canvas Framework', link: '/en/jtbd/' }
            ]
          },
          {
            text: 'SOP Runbooks',
            collapsed: false,
            items: [
              { text: 'SOP Directory', link: '/en/sop/' },
              { text: 'SOP-001: Installation', link: '/en/sop/setup' },
              { text: 'SOP-002: Diagnostics', link: '/en/sop/troubleshooting' }
            ]
          },
          {
            text: 'API Reference',
            items: [
              { text: 'FastAPI Spec', link: '/en/api/' }
            ]
          },
          {
            text: 'Scaffold Deployment',
            items: [
              { text: 'Containers & GKE', link: '/en/deployment' }
            ]
          }
        ]
      }
    }
  },

  // Global Theme Configurations
  themeConfig: {
    logo: '🤖',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kiza101288/ai-workflow-orchestrator' }
    ],
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: 'Pretraži dokumentaciju',
                buttonAriaLabel: 'Pretraži dokumentaciju'
              },
              modal: {
                noResultsText: 'Nema rezultata za',
                resetButtonTitle: 'Resetuj pretragu',
                footer: {
                  selectText: 'izaberi',
                  navigateText: 'navigiraj',
                  closeText: 'zatvori'
                }
              }
            }
          }
        }
      }
    },
    footer: {
      message: 'Izgrađeno sa Nultim Poverenjem i Adversarial Poravnanjem.',
      copyright: 'Copyright © 2026 Antigravity Systems. Rapid Agent Hackathon.'
    }
  }
})
