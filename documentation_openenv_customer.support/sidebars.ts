import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Project',
      items: [
        'project-overview',
        'architecture',
        'environment-loop',
        'reward-and-evaluation',
        'training-and-submission',
      ],
    },
    {
      type: 'category',
      label: 'Hackathon Strategy',
      items: [
        'hackathon-fit',
        'problem-statement',
        'pivot-strategy',
        'judging-and-demo',
      ],
    },
  ],
};

export default sidebars;
