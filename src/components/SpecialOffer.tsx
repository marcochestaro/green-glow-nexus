import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

const SpecialOffer = () => {
  const scrollToContact = () => {
    document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="py-4 bg-gradient-primary animate-fade-in">
      <div className="container px-4">
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-center md:text-left">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary-foreground animate-pulse" />
            <h3 className="text-xl md:text-2xl font-bold text-primary-foreground">
              Limited Time Offer!
            </h3>
          </div>
          <p className="text-primary-foreground/95 text-base md:text-lg">
            Get 20% off your first service when you book this month
          </p>
          <Button 
            onClick={scrollToContact}
            variant="secondary" 
            size="lg"
            className="bg-white text-primary hover:bg-white/90 shadow-large"
          >
            Claim Your Discount
          </Button>
        </div>
      </div>
    </section>
  );
};

export default SpecialOffer;
