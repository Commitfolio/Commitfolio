type ResultExportActionsProps = {
  onPrint: () => void;
};

export function ResultExportActions({ onPrint }: ResultExportActionsProps) {
  return (
    <div className="result-export no-print" aria-label="Result export actions">
      <button className="button" type="button" onClick={onPrint}>
        PDF로 저장/출력
      </button>
      <p className="privacy-note">
        브라우저 출력 창에서 <strong>Save as PDF</strong>를 선택하면 현재 결과 문서를 PDF로 저장할 수 있습니다.
      </p>
    </div>
  );
}
