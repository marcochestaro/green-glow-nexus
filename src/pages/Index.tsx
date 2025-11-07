import Hero from "@/components/Hero";
import SpecialOffer from "@/components/SpecialOffer";
import Services from "@/components/Services";
import Testimonials from "@/components/Testimonials";
import SeasonalTips from "@/components/SeasonalTips";
import Contact from "@/components/Contact";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <SpecialOffer />
      <Services />
      <Testimonials />
      <SeasonalTips />
      <Contact />
      <Footer />
    </div>
  );
};

export default Index;
