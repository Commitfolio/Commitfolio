import type { PortfolioResultListItem } from "../../entities/portfolio-result/portfolio-result.types";

type RecentResultsProps = {
  items: PortfolioResultListItem[];
  onSelectResult: (resultId: string) => void;
};

export function RecentResults({ items, onSelectResult }: RecentResultsProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className="recent-results">
      <h3>Recent results</h3>
      <ul className="event-list" aria-label="Recent portfolio results">
        {items.map((item) => (
          <li key={item.result_id}>
            <button className="link-button" type="button" onClick={() => onSelectResult(item.result_id)}>
              {item.headline}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
