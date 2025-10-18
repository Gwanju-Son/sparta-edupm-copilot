// Mobile nav toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');
if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
        const isActive = navMenu.classList.toggle('active');
        navToggle.setAttribute('aria-expanded', isActive);
    });
    // Close menu when clicking a link
    navMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

// Smooth scroll behavior for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.05)';
    }
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Apply fade-in to project cards and insight cards
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.project-card, .insight-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Optional: Console message for visitors
console.log('%c안녕하세요! 👋', 'font-size: 20px; font-weight: bold; color: #1e3a5f;');
console.log('%c교육·데이터·AI를 잇는 PM 손관주입니다.', 'font-size: 14px; color: #4a90e2;');
console.log('%c함께 성장할 기회를 만들어가고 싶습니다. 연락 주세요!', 'font-size: 14px; color: #6c757d;');


// === Interactive Career Map (vis-network) ===
function ensureVisLoaded() {
    return new Promise((resolve, reject) => {
        if (window.vis && window.vis.Network) return resolve();
        const cdn = document.createElement('script');
        cdn.src = 'https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js';
        cdn.onload = () => resolve();
        cdn.onerror = () => reject(new Error('vis-network CDN 로드 실패'));
        document.head.appendChild(cdn);
    });
}

function initCareerMap() {
    // Career Map 데이터 불러오기 (GitHub Pages 호환 경로)
    return fetch('./data/linkedin_kg.json')
        .then(response => response.json())
        .then(data => {
            // 원본 데이터 보관
            const rawNodes = data.entities.map(e => ({
                id: e.id,
                label: e.name,
                title: `<b>${e.name}</b><br>${e.type}<br>${e.description}`,
                type: e.type,
                group: e.type,
                shape: 'dot',
                size: 22
            }));
            const rawEdges = data.relationships.map(r => ({
                from: r.source,
                to: r.target,
                label: r.relationship,
                font: {align: 'middle'},
                arrows: 'to',
                color: {color:'#3949ab'}
            }));

            const container = document.getElementById('career-graph');
            if (!container) return;
            const nodeDS = new vis.DataSet(rawNodes);
            const edgeDS = new vis.DataSet(rawEdges);
            const networkData = { nodes: nodeDS, edges: edgeDS };
            const options = {
                nodes: {
                    font: { size: 16, color: '#222', face: 'Noto Sans KR' },
                    borderWidth: 2,
                    color: { background: '#e8eaf6', border: '#1a237e', highlight: { background: '#c5cae9', border: '#3949ab' } }
                },
                edges: {
                    color: { color: '#b0bec5', highlight: '#3949ab' },
                    smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.4 },
                    width: 2
                },
                groups: {
                    '인물': { color: { background: '#fffde7', border: '#fbc02d' }, shape: 'ellipse' },
                    '역량': { color: { background: '#e3f2fd', border: '#1976d2' }, shape: 'dot' },
                    '프로그램': { color: { background: '#f3e5f5', border: '#8e24aa' }, shape: 'box' },
                    '교육 프로그램': { color: { background: '#e8f5e9', border: '#388e3c' }, shape: 'box' },
                    '사업체': { color: { background: '#fff3e0', border: '#f57c00' }, shape: 'box' },
                    '교육기관': { color: { background: '#e1f5fe', border: '#0288d1' }, shape: 'box' },
                    '기업': { color: { background: '#ede7f6', border: '#5e35b1' }, shape: 'box' },
                    '습관': { color: { background: '#fce4ec', border: '#d81b60' }, shape: 'star' },
                    '지역': { color: { background: '#f5f5f5', border: '#757575' }, shape: 'hexagon' }
                },
                layout: { hierarchical: { enabled: false } },
                physics: { enabled: true, barnesHut: { gravitationalConstant: -25000, springLength: 180, springConstant: 0.04 } },
                interaction: { hover: true, tooltipDelay: 100, navigationButtons: true, selectable: true }
            };
            const network = new vis.Network(container, networkData, options);

            // 검색 & 필터
            const searchInput = document.getElementById('career-search');
            const filterCheckboxes = document.querySelectorAll('.type-filter');
            const resetBtn = document.getElementById('career-reset');

            function applyFilters() {
                const query = (searchInput?.value || '').trim().toLowerCase();
                const enabledTypes = new Set(
                    Array.from(filterCheckboxes)
                        .filter(cb => cb.checked)
                        .map(cb => cb.value)
                );

                const filteredNodes = rawNodes.filter(n => {
                    const passType = enabledTypes.has(n.type);
                    const passQuery = !query || n.label.toLowerCase().includes(query) || (n.title || '').toLowerCase().includes(query);
                    return passType && passQuery;
                });

                const visibleIds = new Set(filteredNodes.map(n => n.id));
                const filteredEdges = rawEdges.filter(e => visibleIds.has(e.from) && visibleIds.has(e.to));

                nodeDS.update(filteredNodes);
                // 제거된 노드/엣지 반영을 위해 전체 재설정
                nodeDS.clear();
                edgeDS.clear();
                nodeDS.add(filteredNodes);
                edgeDS.add(filteredEdges);
            }

            searchInput?.addEventListener('input', () => {
                applyFilters();
            });
            filterCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));
            resetBtn?.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                filterCheckboxes.forEach(cb => (cb.checked = true));
                // 원본으로 복구
                nodeDS.clear(); edgeDS.clear();
                nodeDS.add(rawNodes); edgeDS.add(rawEdges);
                // 뷰 리셋
                network.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
            });

            // 모달 표시
            const modal = document.getElementById('node-modal');
            const modalBody = document.getElementById('node-modal-body');
            const modalClose = document.getElementById('node-modal-close');
            function openModal(html) {
                if (!modal || !modalBody) return;
                modalBody.innerHTML = html;
                modal.style.display = 'block';
            }
            function closeModal() {
                if (!modal) return;
                modal.style.display = 'none';
            }
            modalClose?.addEventListener('click', closeModal);
            modal?.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const node = rawNodes.find(n => n.id === nodeId);
                    if (node) {
                        const clean = node.title.replace(/<[^>]+>/g, '').replace(/\n/g, '<br>');
                        const html = `
                            <div style="display:flex; flex-direction:column; gap:8px;">
                                <div style="font-size:1.1rem; font-weight:700; color:#111827">${node.label}</div>
                                <div style="font-size:0.95rem; color:#6b7280">유형: ${node.type}</div>
                                <div style="font-size:1rem; color:#334155">${clean}</div>
                            </div>
                        `;
                        openModal(html);
                    }
                }
            });
        });
}

document.addEventListener('DOMContentLoaded', () => {
    // ...기존 코드 유지...

    ensureVisLoaded()
        .then(() => initCareerMap())
        .catch(err => console.error('Career Map 초기화 실패:', err));

    // === Skills (Chart.js) ===
    fetch('./data/matrices.json')
        .then(res => res.json())
        .then(mat => {
            const skills = (mat.skills || []).slice(0);
            const labels = skills.map(s => s.name);
            const data = skills.map(s => s.level);
            const ctx = document.getElementById('skills-radar');
            if (ctx && window.Chart) {
                new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels,
                        datasets: [{
                            label: '숙련도(10점 만점)',
                            data,
                            fill: true,
                            backgroundColor: 'rgba(63,81,181,0.15)',
                            borderColor: '#3f51b5',
                            pointBackgroundColor: '#3f51b5',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: '#3f51b5'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            r: { suggestedMin: 0, suggestedMax: 10, ticks: { stepSize: 2 } }
                        },
                        plugins: { legend: { display: true } }
                    }
                });
            }
            const ul = document.getElementById('skills-list');
            if (ul) {
                ul.innerHTML = skills.map(s => `
                    <li style="background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:12px 14px;">
                        <div style="font-weight:700; color:#1f2937;">${s.name} <span style="color:#6b7280; font-weight:500;">(Lv.${s.level})</span></div>
                        <div style="color:#6b7280;">${s.evidence || ''}</div>
                    </li>
                `).join('');
            }
        })
        .catch(err => console.error('Skills 데이터 로드 실패:', err));

    // === Writing Habit Heatmap ===
    fetch('./data/writing_habit.json')
        .then(res => res.json())
        .then(h => {
            const container = document.getElementById('writing-heatmap');
            const summary = document.getElementById('writing-summary');
            if (!container) return;
            container.innerHTML = '';
            let total = 0; let days = 0; let streak = 0; let maxStreak = 0;
            const monthNames = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            h.months.forEach(m => {
                // 월 라벨
                const label = document.createElement('div');
                label.textContent = monthNames[m.month];
                label.style.gridColumn = 'span 14';
                label.style.color = '#374151';
                label.style.fontWeight = '700';
                label.style.margin = '6px 0 2px 0';
                container.appendChild(label);

                // 날짜 셀
                let prevActive = false;
                m.days.forEach(([day, active]) => {
                    const cell = document.createElement('div');
                    cell.title = `${h.year}-${String(m.month).padStart(2,'0')}-${String(day).padStart(2,'0')} : ${active ? '작성' : '미작성'}`;
                    cell.style.height = '18px';
                    cell.style.borderRadius = '4px';
                    cell.style.border = '1px solid #e5e7eb';
                    cell.style.background = active ? '#34d399' : '#f3f4f6';
                    container.appendChild(cell);
                    total += active ? 1 : 0; days += 1;
                    if (active) { streak += 1; maxStreak = Math.max(maxStreak, streak); }
                    else { streak = 0; }
                });
            });
            if (summary) {
                const rate = days ? Math.round((total / days) * 100) : 0;
                summary.innerHTML = `최근 ${days}일 중 <b>${total}</b>일 작성 · 달성률 <b>${rate}%</b> · 최장 연속 <b>${maxStreak}</b>일`;
            }

            // Update Project Card KPI
            const projectKPI = document.getElementById('writing-project-kpi');
            if (projectKPI) {
                const rate = days ? Math.round((total / days) * 100) : 0;
                projectKPI.innerHTML = `
                    <li>최장 연속 <b>${maxStreak}</b>일, 최근 ${days}일 달성률 <b>${rate}%</b></li>
                    <li>주제 분류/태깅으로 검색성 향상</li>
                    <li>프로젝트 설계/회고 품질 개선에 기여</li>
                `;
            }
        })
        .catch(err => console.error('Writing Habit 데이터 로드 실패:', err));
});
