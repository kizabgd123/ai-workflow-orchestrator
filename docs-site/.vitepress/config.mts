import { defineConfig } from 'vitepress'


export default defineConfig({
  srcDir: '../docs',
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
