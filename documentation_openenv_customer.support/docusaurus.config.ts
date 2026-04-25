import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Support Triage Env Docs',
  tagline: 'Detailed project documentation, evaluation logic, and hackathon positioning',
  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'http://localhost:8000',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/project-docs/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'local-workspace',
  projectName: 'support-triage-env-docs',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: 'Support Triage Env',
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Overview',
        },
        {
          type: 'doc',
          docId: 'hackathon-fit',
          position: 'left',
          label: 'Theme Fit',
        },
        {
          type: 'doc',
          docId: 'problem-statement',
          position: 'left',
          label: 'Problem Statement',
        },
        {
          type: 'doc',
          docId: 'pivot-strategy',
          position: 'left',
          label: 'Pivot Strategy',
        },
      ],
    },
    footer: {
      style: 'light',
      links: [
        {
          title: 'Project',
          items: [
            {
              label: 'Overview',
              to: '/docs/intro',
            },
            {
              label: 'Architecture',
              to: '/docs/architecture',
            },
          ],
        },
        {
          title: 'Hackathon',
          items: [
            {
              label: 'Theme Fit',
              to: '/docs/hackathon-fit',
            },
            {
              label: 'Problem Statement',
              to: '/docs/problem-statement',
            },
            {
              label: 'Pivot Strategy',
              to: '/docs/pivot-strategy',
            },
          ],
        },
        {
          title: 'Execution',
          items: [
            {
              label: 'Training and Submission',
              to: '/docs/training-and-submission',
            },
            {
              label: 'Judging and Demo',
              to: '/docs/judging-and-demo',
            },
          ],
        },
      ],
      copyright: `Built for the Support_triage_env project with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
