import { Button } from '@/components/Button';
import { Container, Spacer } from '@/components/Layout';
import Wrapper from '@/components/Layout/Wrapper';
import { SubmissionPost } from '@/components/Submit';
import { Text } from '@/components/Text';
import { useSubmitProfile } from '@/lib/submission';
import Link from 'next/link';
import styles from './UserSubmits.module.css';

const UserSubmits = ({ user }) => {
  const { data, size, setSize, isLoadingMore, isReachingEnd } =
    useSubmitProfile({
      creatorId: user._id,
    });
  const submissions = data
    ? data.reduce((acc, val) => [...acc, ...val.submissions], [])
    : [];

  return (
    <div className={styles.root}>
      <Spacer axis="vertical" size={1} />
      <Wrapper>
        {submissions.map((submission) => (
          <Link
            key={submission._id}
            href={`/user/${submission.creator.username}/submission/${submission._id}`}
          >
            <a className={styles.wrap}>
              <SubmissionPost className={styles.post} submission={submission} />
            </a>
          </Link>
        ))}
        <Container justifyContent="center">
          {isReachingEnd ? (
            <Text color="secondary">No more submission are found</Text>
          ) : (
            <Button
              variant="ghost"
              type="success"
              loading={isLoadingMore}
              onClick={() => setSize(size + 1)}
            >
              Load more
            </Button>
          )}
        </Container>
      </Wrapper>
    </div>
  );
};

export default UserSubmits;
