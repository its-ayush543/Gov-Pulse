import { NewsItem, departmentNames } from "@/data/newsData";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "lucide-react";

interface NewsCardProps {
  news: NewsItem;
  onClick: () => void;
  showDepartment?: boolean;
}

const NewsCard = ({ news, onClick, showDepartment = false }: NewsCardProps) => {
  const sentimentColors = {
    positive: "bg-sentiment-positive text-white",
    negative: "bg-sentiment-negative text-white",
    neutral: "bg-sentiment-neutral text-white",
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <Card
      onClick={onClick}
      className="group cursor-pointer overflow-hidden bg-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 animate-scale-in border border-border"
    >
      <div className="p-6">
        {showDepartment && (
          <Badge variant="outline" className="mb-3">
            {departmentNames[news.department]}
          </Badge>
        )}
        <div className="flex items-start justify-between gap-4 mb-4">
          <h3 className="text-lg font-semibold text-card-foreground group-hover:text-primary transition-colors line-clamp-2">
            {news.headline}
          </h3>
        </div>

        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
          {news.summary}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>{formatDate(news.publishedAt)}</span>
          </div>

          <Badge
            className={`${sentimentColors[news.sentiment]} capitalize text-xs font-medium`}
          >
            {news.sentiment}
          </Badge>
        </div>
      </div>

      <div className="h-1 bg-gradient-primary transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
    </Card>
  );
};

export default NewsCard;
