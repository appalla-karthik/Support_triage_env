import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className={clsx('container', styles.heroShell)}>
        <div className={styles.heroCopy}>
          <div className={styles.eyebrow}>OpenEnv project docs</div>
          <Heading as="h1" className={styles.heroTitle}>
            {siteConfig.title}
          </Heading>
          <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
          <div className={styles.buttonRow}>
            <Link className="button button--primary button--lg" to="/docs/intro">
              Start with the project overview
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/hackathon-fit">
              See the best Round 2 theme fit
            </Link>
          </div>
        </div>
        <div className={styles.heroPanel}>
          <div className={styles.metricCard}>
            <span>Primary fit</span>
            <strong>Theme 3.1: World Modeling</strong>
            <p>
              Professional workflow simulation with dynamic state, policy
              constraints, and real task sequencing.
            </p>
          </div>
          <div className={styles.metricGrid}>
            <div className={styles.metricTile}>
              <span>Current tasks</span>
              <strong>3</strong>
            </div>
            <div className={styles.metricTile}>
              <span>Core loop</span>
              <strong>Reset - Step - State</strong>
            </div>
            <div className={styles.metricTile}>
              <span>Strong secondary fit</span>
              <strong>Long-horizon planning</strong>
            </div>
            <div className={styles.metricTile}>
              <span>Best pivot</span>
              <strong>Support ops control tower</strong>
            </div>
          </div>
        </div>
      </div>
      <div className={clsx('container', styles.ribbonRow)}>
        <div className={styles.ribbon}>
          <span>What this site gives you</span>
          <p>
            A detailed walkthrough of the current `Support_triage_env` repo, a
            grounded analysis of how it matches the hackathon themes, and a
            practical plan to pivot it into a stronger finalist-style submission.
          </p>
        </div>
      </div>
    </header>
  );
}

function HomeCallout() {
  return (
    <section className={styles.calloutSection}>
      <div className="container">
        <div className={styles.calloutBox}>
          <div>
            <p className={styles.calloutLabel}>Recommended positioning</p>
            <Heading as="h2" className={styles.calloutTitle}>
              Pitch this as a professional support-operations world model, then
              extend it with longer horizons and multi-actor coordination.
            </Heading>
          </div>
          <div className={styles.calloutActions}>
            <Link className="button button--primary button--lg" to="/docs/problem-statement">
              Read the proposed problem statement
            </Link>
            <Link className="button button--outline button--lg" to="/docs/pivot-strategy">
              Open the pivot roadmap
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Documentation and hackathon strategy for the Support_triage_env OpenEnv project.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomeCallout />
      </main>
    </Layout>
  );
}
