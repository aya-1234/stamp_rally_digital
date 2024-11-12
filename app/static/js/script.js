document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');
    const button = document.getElementById('showButton');
    const content = document.getElementById('hiddenContent');
  
    button.addEventListener('click', () => {
      if (content.style.display === 'none') {
        content.style.display = 'block'; // 表示
        button.textContent = 'クリックして隠す';
      } else {
        content.style.display = 'none'; // 非表示
        button.textContent = 'クリックして表示';
      }
    }); // ここで閉じカッコを追加
  
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.target;
  
        // すべてのタブとコンテンツを非アクティブにする
        tabs.forEach(t => t.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));
  
        // クリックされたタブと対応するコンテンツをアクティブにする
        tab.classList.add('active');
        document.getElementById(target).classList.add('active');
      });
    });
  });