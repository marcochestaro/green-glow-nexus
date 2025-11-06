import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Leaf, Scissors, TreePine, Droplets } from "lucide-react";
import serviceMowing from "@/assets/service-mowing.jpg";
import servicePruning from "@/assets/service-pruning.jpg";
import serviceDesign from "@/assets/service-design.jpg";
import serviceFertilize from "@/assets/service-fertilize.jpg";

const services = [
  {
    title: "Lawn Mowing & Maintenance",
    description: "Regular mowing, edging, and trimming to keep your lawn looking pristine year-round.",
    icon: Leaf,
    image: serviceMowing,
    details: "Weekly or bi-weekly service includes precision mowing, professional edging, trimming around obstacles, and debris cleanup."
  },
  {
    title: "Pruning & Trimming",
    description: "Expert pruning of trees, shrubs, and hedges to promote healthy growth and beautiful shapes.",
    icon: Scissors,
    image: servicePruning,
    details: "Seasonal pruning services that enhance plant health, improve aesthetics, and maintain proper clearances from structures."
  },
  {
    title: "Landscape Design",
    description: "Custom landscape designs that transform your outdoor space into a stunning retreat.",
    icon: TreePine,
    image: serviceDesign,
    details: "From concept to completion, we create personalized designs with native plants, hardscaping, and sustainable features."
  },
  {
    title: "Fertilization & Weed Control",
    description: "Professional treatments to nourish your lawn and eliminate unwanted weeds.",
    icon: Droplets,
    image: serviceFertilize,
    details: "Customized fertilization programs and eco-friendly weed control solutions for a lush, healthy lawn."
  }
];

const Services = () => {
  const [expandedCard, setExpandedCard] = useState<number | null>(null);

  return (
    <section id="services" className="py-20 bg-muted/30">
      <div className="container px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Our Services
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Comprehensive lawn care and landscaping solutions tailored to your needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((service, index) => {
            const Icon = service.icon;
            const isExpanded = expandedCard === index;
            
            return (
              <Card
                key={index}
                className="group cursor-pointer transition-all duration-300 hover:shadow-large animate-slide-up border-border/50"
                style={{ animationDelay: `${index * 100}ms` }}
                onClick={() => setExpandedCard(isExpanded ? null : index)}
              >
                <CardContent className="p-0">
                  <div className="relative overflow-hidden rounded-t-lg h-48">
                    <img 
                      src={service.image} 
                      alt={service.title}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-40 transition-opacity duration-300" />
                    <div className="absolute top-4 right-4 bg-primary/90 backdrop-blur-sm p-3 rounded-full">
                      <Icon className="h-6 w-6 text-primary-foreground" />
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                      {service.title}
                    </h3>
                    <p className="text-muted-foreground text-sm mb-4">
                      {service.description}
                    </p>
                    
                    <div 
                      className={`overflow-hidden transition-all duration-300 ${
                        isExpanded ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
                      }`}
                    >
                      <div className="pt-4 border-t border-border/50">
                        <p className="text-sm text-foreground/80">
                          {service.details}
                        </p>
                      </div>
                    </div>
                    
                    <button className="text-sm text-primary font-medium hover:text-secondary transition-colors mt-4">
                      {isExpanded ? "Show Less" : "Learn More"} →
                    </button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Services;
