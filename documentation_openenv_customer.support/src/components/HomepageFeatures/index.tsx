import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  kicker: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    kicker: 'Project',
    title: 'Grounded enterprise workflow simulation',
    description: (
      <>
        `Support_triage_env` already simulates realistic support queues, typed
        actions, policy constraints, and deterministic grading. That makes it a
        strong foundation instead of just a pitch concept.
      </>
    ),
  },
  {
    kicker: 'Theme fit',
    title: 'Best aligned with World Modeling plus Long Horizon',
    description: (
      <>
        The current repo maps most naturally to Theme 3.1 because agents must
        maintain state, act safely in a professional workflow, and sequence
        actions against a partially observable queue.
      </>
    ),
  },
  {
    kicker: 'Submission strategy',
    title: 'Stronger if framed as a support operations control tower',
    description: (
      <>
        The recommended pivot is to evolve the environment from single-ticket
        triage into a multi-team support command center with SLA clocks, policy
        drift, delayed outcomes, and internal specialist handoffs.
      </>
    ),
  },
  {
    kicker: 'Evaluation',
    title: 'Reward logic is already one of the project strengths',
    description: (
      <>
        The repo includes deterministic graders, shaped rewards, penalties for
        unsafe behavior, and reproducible tasks. That is exactly the kind of
        measurable environment foundation judges usually want to see.
      </>
    ),
  },
];

function Feature({title, kicker, description}: FeatureItem) {
  return (
    <div className={clsx('col col--6')}>
      <div className={styles.featureCard}>
        <div className={styles.featureKicker}>{kicker}</div>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.sectionIntro}>
          <p>What the documentation covers</p>
          <Heading as="h2">Built to help you explain the project and improve it</Heading>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
