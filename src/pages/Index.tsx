import Nav from '@/components/landing/Nav';
import Hero from '@/components/landing/Hero';
import Divider from '@/components/landing/Divider';
import Story from '@/components/landing/Story';
import WhatYouGet from '@/components/landing/WhatYouGet';
import FinalCTA from '@/components/landing/FinalCTA';
import Footer from '@/components/landing/Footer';

const Index = () => {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Divider />
        <Story />
        <Divider />
        <WhatYouGet />
        <Divider />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
};

export default Index;
