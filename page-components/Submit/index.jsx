import { Spacer } from '@/components/Layout';
import styles from './Submit.module.css';
import SubmitForm from './SubmitForm';

export const Submit = () => {
  return (
    <div className={styles.root}>
      <Spacer size={1} axis="vertical" />
      <SubmitForm />
    </div>
  );
};
