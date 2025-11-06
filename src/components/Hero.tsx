import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import heroImage from "@/assets/hero-lawn-natural.jpg";

const Hero = () => {
  const scrollToContact = () => {
    document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat"
        }}
      >
        <div className="absolute inset-0 bg-gradient-overlay" />
      </div>

      {/* Content */}
      <div className="container relative z-10 px-4 py-20 md:py-32 text-center">
        <div className="max-w-4xl mx-auto animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-lg">
            Transform Your Outdoor Space
          </h1>
          <p className="text-xl md:text-2xl text-white/95 mb-8 drop-shadow-md max-w-2xl mx-auto">
            Professional landscaping and lawn care services that bring your vision to life
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg" 
              onClick={scrollToContact}
              className="bg-accent hover:bg-accent/90 text-accent-foreground shadow-large group"
            >
              Get Your Free Quote Today
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => document.getElementById("services")?.scrollIntoView({ behavior: "smooth" })}
              className="bg-white/10 backdrop-blur-sm text-white border-white/30 hover:bg-white/20"
            >
              Explore Services
            </Button>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-float">
        <div className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center p-2">
          <div className="w-1 h-3 bg-white/70 rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
};

export default Hero;
