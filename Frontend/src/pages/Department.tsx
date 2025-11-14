import { useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import Navigation from "@/components/Navigation";
import NewsCard from "@/components/NewsCard";
import NewsDetailModal from "@/components/NewsDetailModal";
import {
  Department as DepartmentType,
  departmentNames,
  getNewsBySentiment,
  NewsItem,
  Sentiment,
} from "@/data/newsData";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Department = () => {
  const { name } = useParams<{ name: DepartmentType }>();
  const [selectedSentiment, setSelectedSentiment] = useState<Sentiment | "all">("all");
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const departmentName = name ? departmentNames[name] : "";
  const news = useMemo(
    () => (name ? getNewsBySentiment(name, selectedSentiment) : []),
    [name, selectedSentiment]
  );

  const handleNewsClick = (newsItem: NewsItem) => {
    setSelectedNews(newsItem);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setTimeout(() => setSelectedNews(null), 200);
  };

  if (!name || !departmentNames[name]) {
    return (
      <div className="min-h-screen bg-gradient-hero">
        <Navigation />
        <div className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-4xl font-bold text-foreground">Department not found</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-hero">
      <Navigation />

      <div className="container mx-auto px-4 py-12">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-foreground mb-2">{departmentName}</h1>
          <p className="text-muted-foreground">
            Latest news and public sentiment analysis
          </p>
        </div>

        <div className="mb-8 animate-slide-up">
          <Tabs
            value={selectedSentiment}
            onValueChange={(value) => setSelectedSentiment(value as Sentiment | "all")}
          >
            <TabsList className="bg-card border border-border">
              <TabsTrigger value="all">All News</TabsTrigger>
              <TabsTrigger value="positive">Positive</TabsTrigger>
              <TabsTrigger value="negative">Negative</TabsTrigger>
              <TabsTrigger value="neutral">Neutral</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {news.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground text-lg">
              No news found for this filter.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {news.map((newsItem, index) => (
              <div
                key={newsItem.id}
                style={{
                  animationDelay: `${index * 100}ms`,
                }}
                className="animate-scale-in"
              >
                <NewsCard news={newsItem} onClick={() => handleNewsClick(newsItem)} />
              </div>
            ))}
          </div>
        )}
      </div>

      <NewsDetailModal news={selectedNews} open={modalOpen} onClose={handleCloseModal} />
    </div>
  );
};

export default Department;
