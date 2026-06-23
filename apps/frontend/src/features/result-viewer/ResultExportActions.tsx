type ResultExportActionsProps = {
  onPrint: () => void;
};

export function ResultExportActions({ onPrint }: ResultExportActionsProps) {
  return (
    <div className="result-export no-print" aria-label="Result export actions">
      <div>
        <span className="eyebrow subtle">내보내기</span>
        <h3>문서 출력</h3>
      </div>
      <div className="action-row">
        <button className="button secondary" type="button" onClick={onPrint}>
          PDF로 저장/출력
        </button>
      </div>
      <p className="privacy-note">
        브라우저 출력 창에서 <strong>Save as PDF</strong>를 선택하면 현재 결과 문서를 PDF로 저장할 수 있습니다.
      </p>
    </div>
  );
}
