/* 문제은행 데이터만 운영 도메인에서 Pi SSD로 분리한다. 로컬 개발과 기존 주소는 상대 경로를 쓴다. */
(function () {
  var origin = location.hostname==='solvi.win' ? 'https://bank.solvi.win' : '';
  window.SOLVI_BANK_ORIGIN = origin;
  window.bankUrl = function (relativePath) {
    return origin ? origin + '/' + String(relativePath).replace(/^\/+/, '') : relativePath;
  };
  document.write('<script src="' + window.bankUrl('bank/data.js?v=1') + '"><\\/script>');
}());
