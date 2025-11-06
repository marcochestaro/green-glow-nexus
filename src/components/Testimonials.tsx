import { Card, CardContent } from "@/components/ui/card";
import { Star } from "lucide-react";
import { useState, useEffect } from "react";

const testimonials = [
  {
    name: "Sarah Mitchell",
    location: "Riverside",
    rating: 5,
    text: "Absolutely transformed our backyard! The team was professional, punctual, and the results exceeded our expectations. Our lawn has never looked better.",
  },
  {
    name: "James Rodriguez",
    location: "Oak Park",
    rating: 5,
    text: "Best landscaping service in the area. They designed a beautiful garden that perfectly matched our vision. Highly recommend their expertise!",
  },
  {
    name: "Emily Chen",
    location: "Meadowbrook",
    rating: 5,
    text: "Outstanding service from start to finish. The weekly maintenance keeps our property looking immaculate. Worth every penny!",
  },
];

const Testimonials = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="py-20 bg-gradient-primary">
      <div className="container px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            What Our Clients Say
          </h2>
          <p className="text-lg text-primary-foreground/90 max-w-2xl mx-auto">
            Don't just take our word for it - hear from our satisfied customers
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="bg-white/95 backdrop-blur-sm shadow-large border-0">
            <CardContent className="p-8 md:p-12">
              <div className="flex justify-center mb-6">
                {[...Array(testimonials[currentIndex].rating)].map((_, i) => (
                  <Star key={i} className="h-6 w-6 fill-accent text-accent" />
                ))}
              </div>
              
              <p className="text-lg md:text-xl text-foreground text-center mb-8 italic">
                "{testimonials[currentIndex].text}"
              </p>
              
              <div className="text-center">
                <p className="font-semibold text-foreground text-lg">
                  {testimonials[currentIndex].name}
                </p>
                <p className="text-muted-foreground">
                  {testimonials[currentIndex].location}
                </p>
              </div>

              <div className="flex justify-center gap-2 mt-8">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentIndex(index)}
                    className={`h-2 rounded-full transition-all duration-300 ${
                      index === currentIndex 
                        ? "w-8 bg-primary" 
                        : "w-2 bg-primary/30 hover:bg-primary/50"
                    }`}
                    aria-label={`View testimonial ${index + 1}`}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
