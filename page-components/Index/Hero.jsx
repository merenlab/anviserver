import { ButtonLink } from '@/components/Button';
import { Container, Spacer, Wrapper } from '@/components/Layout';
import Link from 'next/link';
import styles from './Hero.module.css';
import Image from 'next/image';
import Footer from '../../components/Layout/Footer';

const Hero = () => {
  return (
    <Wrapper>
      <div>
        <div className={styles.anvihero}>
          <h1 className={styles.title}>
            <span className={styles.anvi}>Anvi</span>
            <span className={styles.server}>Server</span>
          </h1>
          <Image
            className={styles.image}
            src="/images/anvi-dark.png"
            alt="anvio dark"
            width={350}
            height={350}
            priority="false"
            placeholder="anviserver"
          />
        </div>
        <Container justifyContent="center" className={styles.buttons}>
          <Container>
            <Link passHref href="/feed">
              <ButtonLink className={styles.button}>Explore Feed</ButtonLink>
            </Link>
          </Container>
          <Spacer axis="horizontal" size={1} />
          <Container>
            <Link passHref href="/submit">
              <ButtonLink type="secondary" className={styles.button}>
                Submit
              </ButtonLink>
            </Link>
          </Container>
        </Container>
        <p className={styles.subtitle}>
          An open-source, community-driven analysis and visualization platform
          for microbial &apos;omics.
        </p>
      </div>
      <Footer />
    </Wrapper>
  );
};

export default Hero;
