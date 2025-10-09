import { NewsItem } from "@/data/newsData";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Calendar, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NewsDetailModalProps {
  news: NewsItem | null;
  open: boolean;
  onClose: () => void;
}

const NewsDetailModal = ({ news, open, onClose }: NewsDetailModalProps) => {
  if (!news) return null;

  const sentimentColors = {
    positive: "bg-sentiment-positive text-white",
    negative: "bg-sentiment-negative text-white",
    neutral: "bg-sentiment-neutral text-white",
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto bg-card/95 backdrop-blur-xl border-border">
        <DialogHeader className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <DialogTitle className="text-2xl font-bold text-card-foreground leading-tight">
              {news.headline}
            </DialogTitle>
            <Badge
              className={`${sentimentColors[news.sentiment]} capitalize shrink-0`}
            >
              {news.sentiment}
            </Badge>
          </div>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(news.publishedAt)}</span>
            </div>
            <a
              href={news.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-primary hover:underline"
            >
              <span>{news.source}</span>
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-6">
          <div className="bg-muted/50 p-4 rounded-lg border border-border">
            <p className="text-muted-foreground italic">{news.summary}</p>
          </div>

          <div className="prose prose-sm max-w-none">
            <p className="text-card-foreground leading-relaxed whitespace-pre-line">
              {news.content}
            </p>
          </div>

          <div className="pt-4 border-t border-border">
            <Button asChild variant="outline" className="w-full">
              <a
                href={news.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2"
              >
                Read Full Article
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default NewsDetailModal;
