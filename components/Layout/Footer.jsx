import { TextLink } from '@/components/Text';
import styles from './Footer.module.css';
import Spacer from './Spacer';
import Wrapper from './Wrapper';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDiscord, faGithub } from '@fortawesome/free-brands-svg-icons';
import Link from 'next/link';

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <Wrapper>
        <Spacer size={1} axis="vertical" />
        <div className={styles.icon}>
          <Link passHref href="https://github.com/merenlab/anvio">
            <FontAwesomeIcon icon={faGithub} className={styles.github} />
          </Link>
          <Link passHref href="https://discord.com/invite/C6He6mSNY4">
            <FontAwesomeIcon icon={faDiscord} />
          </Link>
        </div>
        <hr />
        <div>
          <span> {new Date().getFullYear()} </span>
          <TextLink href="https://anvio.org/people/" color="link">
            Merenlab
          </TextLink>
        </div>
      </Wrapper>
    </footer>
  );
};

export default Footer;
