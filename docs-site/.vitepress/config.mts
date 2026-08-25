import { defineConfig } from 'vitepress'






export default defineConfig({


  srcDir: '../docs',
  base: process.env.GITHUB_ACTIONS ? '/ai-workflow-orchestrator/' : '/',


  vite: {


    resolve: { dedupe: ['vue'] }


  },


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


          { text: 'Poetna', link: '/' },


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

