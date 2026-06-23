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
      <div>
        <span className="eyebrow subtle">히스토리</span>
        <h3>최근 결과</h3>
      </div>
      <ul className="recent-result-list" aria-label="최근 포트폴리오 결과">
        {items.map((item) => (
          <li key={item.result_id}>
            <button className="recent-result-button" type="button" onClick={() => onSelectResult(item.result_id)}>
              {item.headline}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
