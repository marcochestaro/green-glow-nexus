import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Mail, Phone, MapPin, Send } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Contact = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    service: "",
    message: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Quote Request Received!",
      description: "We'll get back to you within 24 hours.",
    });
    setFormData({ name: "", email: "", phone: "", service: "", message: "" });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <section id="contact" className="py-20 bg-background">
      <div className="container px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Get Your Free Quote
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Ready to transform your outdoor space? Contact us today for a free consultation
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          {/* Contact Form */}
          <Card className="shadow-medium border-border/50">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Input
                    name="name"
                    placeholder="Your Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="border-input focus:ring-primary"
                  />
                </div>
                
                <div className="grid sm:grid-cols-2 gap-4">
                  <Input
                    name="email"
                    type="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="border-input focus:ring-primary"
                  />
                  <Input
                    name="phone"
                    type="tel"
                    placeholder="Phone Number"
                    value={formData.phone}
                    onChange={handleChange}
                    className="border-input focus:ring-primary"
                  />
                </div>

                <div>
                  <select
                    name="service"
                    value={formData.service}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:ring-2 focus:ring-primary focus:outline-none"
                    required
                  >
                    <option value="">Select a Service</option>
                    <option value="mowing">Lawn Mowing & Maintenance</option>
                    <option value="pruning">Pruning & Trimming</option>
                    <option value="design">Landscape Design</option>
                    <option value="fertilization">Fertilization & Weed Control</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <Textarea
                    name="message"
                    placeholder="Tell us about your project..."
                    value={formData.message}
                    onChange={handleChange}
                    rows={5}
                    className="border-input focus:ring-primary resize-none"
                  />
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-primary hover:bg-secondary text-primary-foreground group"
                  size="lg"
                >
                  Send Request
                  <Send className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Info */}
          <div className="space-y-8">
            <Card className="shadow-soft hover:shadow-medium transition-shadow border-border/50">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Phone className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground text-lg mb-1">Phone</h3>
                  <p className="text-muted-foreground">(555) 123-4567</p>
                  <p className="text-sm text-muted-foreground">Mon-Sat: 7AM - 7PM</p>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-medium transition-shadow border-border/50">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="bg-accent/10 p-3 rounded-lg">
                  <Mail className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground text-lg mb-1">Email</h3>
                  <p className="text-muted-foreground">info@greenlawncare.com</p>
                  <p className="text-sm text-muted-foreground">24/7 Response Time</p>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-soft hover:shadow-medium transition-shadow border-border/50">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="bg-secondary/10 p-3 rounded-lg">
                  <MapPin className="h-6 w-6 text-secondary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground text-lg mb-1">Service Area</h3>
                  <p className="text-muted-foreground">Serving Greater Metro Area</p>
                  <p className="text-sm text-muted-foreground">Within 50 mile radius</p>
                </div>
              </CardContent>
            </Card>

            <div className="bg-gradient-primary rounded-lg p-8 text-center">
              <h3 className="text-2xl font-bold text-primary-foreground mb-2">
                Limited Time Offer!
              </h3>
              <p className="text-primary-foreground/90 mb-4">
                Get 20% off your first service when you book this month
              </p>
              <Button 
                variant="secondary" 
                size="lg"
                className="bg-white text-primary hover:bg-white/90"
              >
                Claim Your Discount
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
