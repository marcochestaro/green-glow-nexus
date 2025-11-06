import { Card, CardContent } from "@/components/ui/card";
import { Leaf, Snowflake, Sun, Wind } from "lucide-react";

const getCurrentSeason = () => {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return "spring";
  if (month >= 5 && month <= 7) return "summer";
  if (month >= 8 && month <= 10) return "fall";
  return "winter";
};

const seasonalContent = {
  spring: {
    title: "Spring Lawn Care Tips",
    icon: Leaf,
    tips: [
      "Start with a thorough spring cleanup to remove winter debris",
      "Apply pre-emergent weed control early in the season",
      "Begin regular mowing when grass reaches 3-4 inches",
      "Aerate and overseed thin or damaged areas",
    ],
    color: "text-secondary",
    bgColor: "bg-secondary/10",
  },
  summer: {
    title: "Summer Lawn Care Tips",
    icon: Sun,
    tips: [
      "Water deeply but less frequently (1-1.5 inches per week)",
      "Mow higher during hot weather to protect roots",
      "Apply summer fertilizer for sustained growth",
      "Watch for signs of pests and treat promptly",
    ],
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
  fall: {
    title: "Fall Lawn Care Tips",
    icon: Wind,
    tips: [
      "Rake leaves regularly to prevent lawn suffocation",
      "Apply fall fertilizer to strengthen roots",
      "Overseed bare patches for spring recovery",
      "Continue mowing until grass stops growing",
    ],
    color: "text-earth-dark",
    bgColor: "bg-earth/10",
  },
  winter: {
    title: "Winter Lawn Care Tips",
    icon: Snowflake,
    tips: [
      "Avoid walking on frozen grass to prevent damage",
      "Clear debris and branches after storms",
      "Plan your spring landscaping projects",
      "Service and maintain lawn equipment",
    ],
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
};

const SeasonalTips = () => {
  const season = getCurrentSeason();
  const content = seasonalContent[season];
  const Icon = content.icon;

  return (
    <section className="py-20 bg-muted/20">
      <div className="container px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="shadow-large border-border/50 overflow-hidden">
            <div className={`${content.bgColor} p-6 border-b border-border/50`}>
              <div className="flex items-center gap-4">
                <div className={`${content.bgColor} p-4 rounded-full border-2 border-current ${content.color}`}>
                  <Icon className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-foreground">
                    {content.title}
                  </h2>
                  <p className="text-muted-foreground">
                    Expert advice for the current season
                  </p>
                </div>
              </div>
            </div>
            
            <CardContent className="p-8">
              <ul className="space-y-4">
                {content.tips.map((tip, index) => (
                  <li 
                    key={index} 
                    className="flex items-start gap-3 animate-slide-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className={`mt-1 h-2 w-2 rounded-full ${content.color} flex-shrink-0`} />
                    <p className="text-foreground leading-relaxed">{tip}</p>
                  </li>
                ))}
              </ul>

              <div className="mt-8 p-4 bg-muted/50 rounded-lg border border-border/50">
                <p className="text-sm text-muted-foreground text-center">
                  💡 <strong>Pro Tip:</strong> Schedule your next service now to stay ahead of the season!
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default SeasonalTips;
