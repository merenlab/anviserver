import { Avatar } from '@/components/Avatar';
import { Container } from '@/components/Layout';
import { format } from '@lukeed/ms';
import clsx from 'clsx';
import Link from 'next/link';
import { useMemo } from 'react';
import styles from './SubmissionPost.module.css';

const SubmissionPost = ({ submission, className }) => {
  const timestampTxt = useMemo(() => {
    const diff = Date.now() - new Date(submission.createdAt).getTime();
    if (diff < 1 * 60 * 1000) return 'Just now';
    return `${format(diff, true)} ago`;
  }, [submission.createdAt]);
  return (
    <div className={clsx(styles.root, className)}>
      <Link href={`/user/${submission.creator.username}`}>
        <a>
          <Container className={styles.creator}>
            <Avatar
              size={36}
              url={submission.creator.profilePicture}
              username={submission.creator.username}
            />
            <Container column className={styles.meta}>
              <p className={styles.name}>{submission.creator.name}</p>
              <p className={styles.username}>{submission.creator.username}</p>
            </Container>
          </Container>
        </a>
      </Link>
      <div className={styles.wrap}>
        <p className={styles.title}>{submission.title}</p>
        <p className={styles.desc}>{submission.desc}</p>
      </div>
      <div className={styles.wrap}>
        <time
          dateTime={String(submission.createdAt)}
          className={styles.timestamp}
        >
          {timestampTxt}
        </time>
      </div>
    </div>
  );
};

export default SubmissionPost;
