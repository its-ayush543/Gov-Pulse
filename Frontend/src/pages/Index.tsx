import { Link } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Scale,
  Shield,
  Users,
  Microscope,
  Trophy,
  Heart,
  Music,
  TrendingUp,
  Swords,
  Globe,
  ArrowRight,
  BarChart3,
} from "lucide-react";
import { Department, departmentNames } from "@/data/newsData";

const departmentIcons: Record<Department, any> = {
  judiciary: Scale,
  crime: Shield,
  politics: Users,
  science: Microscope,
  sports: Trophy,
  health: Heart,
  entertainment: Music,
  economy: TrendingUp,
  defence: Swords,
  "foreign-affairs": Globe,
};

const Index = () => {
  const departments = Object.keys(departmentNames) as Department[];

  return (
    <div className="min-h-screen bg-gradient-hero">
      <Navigation />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center animate-fade-in">
        <Badge className="mb-6 bg-primary/10 text-primary hover:bg-primary/20 border-primary/20">
          <BarChart3 className="h-3 w-3 mr-1" />
          Real-time Sentiment Analysis
        </Badge>

        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight">
          Understanding Public Sentiment
          <br />
          <span className="bg-gradient-primary bg-clip-text text-transparent">
            with GovPulse AI
          </span>
        </h1>

        <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
          Track and analyze public reaction to government policies across 10 key departments.
          AI-powered sentiment analysis helps agencies understand citizen perspectives in real-time.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
          <Button size="lg" asChild className="bg-gradient-primary shadow-glow hover:shadow-glow">
            <Link to="/all-news">
              Browse All News
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a href="#departments">View All Categories</a>
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="bg-card p-6 rounded-lg border border-border shadow-card">
            <div className="text-3xl font-bold text-primary mb-2">10</div>
            <div className="text-sm text-muted-foreground">Departments</div>
          </div>
          <div className="bg-card p-6 rounded-lg border border-border shadow-card">
            <div className="text-3xl font-bold text-primary mb-2">1000+</div>
            <div className="text-sm text-muted-foreground">News Articles</div>
          </div>
          <div className="bg-card p-6 rounded-lg border border-border shadow-card">
            <div className="text-3xl font-bold text-primary mb-2">Real-time</div>
            <div className="text-sm text-muted-foreground">Analysis</div>
          </div>
          <div className="bg-card p-6 rounded-lg border border-border shadow-card">
            <div className="text-3xl font-bold text-primary mb-2">AI-Powered</div>
            <div className="text-sm text-muted-foreground">Insights</div>
          </div>
        </div>
      </section>

      {/* Departments Grid */}
      <section id="departments" className="container mx-auto px-4 py-20">
        <div className="text-center mb-12 animate-slide-up">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Explore Departments
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Click on any department to view the latest news and sentiment analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {departments.map((dept, index) => {
            const Icon = departmentIcons[dept];
            return (
              <Link
                key={dept}
                to={`/department/${dept}`}
                className="group"
                style={{
                  animationDelay: `${index * 50}ms`,
                }}
              >
                <div className="bg-card p-6 rounded-xl border border-border shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-2 animate-scale-in">
                  <div className="flex flex-col items-center text-center gap-4">
                    <div className="h-14 w-14 bg-gradient-primary rounded-lg flex items-center justify-center shadow-glow group-hover:scale-110 transition-transform">
                      <Icon className="h-7 w-7 text-primary-foreground" />
                    </div>
                    <h3 className="font-semibold text-card-foreground group-hover:text-primary transition-colors">
                      {departmentNames[dept]}
                    </h3>
                  </div>
                  <div className="mt-4 h-1 bg-gradient-primary transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 rounded-full" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-card rounded-2xl border border-border shadow-card p-8 md:p-12 animate-fade-in">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              How GovPulse AI Works
            </h2>
            <p className="text-lg text-muted-foreground">
              Advanced AI technology for comprehensive sentiment analysis
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto mb-4 shadow-glow">
                <Globe className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="font-semibold text-lg text-card-foreground mb-2">
                News Aggregation
              </h3>
              <p className="text-muted-foreground">
                Automatically scrape and collect news from trusted sources across all departments
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto mb-4 shadow-glow">
                <BarChart3 className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="font-semibold text-lg text-card-foreground mb-2">
                Sentiment Analysis
              </h3>
              <p className="text-muted-foreground">
                AI-powered analysis categorizes public sentiment as positive, negative, or neutral
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto mb-4 shadow-glow">
                <Shield className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="font-semibold text-lg text-card-foreground mb-2">
                Agency Insights
              </h3>
              <p className="text-muted-foreground">
                Government agencies gain actionable insights to improve policy communication
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center border-t border-border">
        <p className="text-muted-foreground">
          © 2025 GovPulse AI. Empowering governments with data-driven insights.
        </p>
      </footer>
    </div>
  );
};

export default Index;
