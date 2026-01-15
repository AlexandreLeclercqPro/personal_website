// Animation au scroll
document.addEventListener('DOMContentLoaded', function() {
    // Observer pour les animations au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observer toutes les sections et cards
    const sections = document.querySelectorAll('.section');
    const cards = document.querySelectorAll('.card');
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Animation des tags de compétences
    const skillTags = document.querySelectorAll('.skill-tag');
    skillTags.forEach((tag, index) => {
        tag.style.animationDelay = `${index * 0.05}s`;
        tag.classList.add('fade-in-tag');
    });

    // Smooth scroll pour les liens internes (si vous en ajoutez)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Effet parallax léger sur le header
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.3;
            header.style.transform = `translate3d(0, ${rate}px, 0)`;
        });
    }

    // Animation de typing pour le titre (optionnel)
    const titleElement = document.querySelector('.title');
    if (titleElement && titleElement.textContent) {
        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        let index = 0;

        function typeWriter() {
            if (index < originalText.length) {
                titleElement.textContent += originalText.charAt(index);
                index++;
                setTimeout(typeWriter, 50);
            }
        }

        // Démarrer l'animation après un court délai
        setTimeout(typeWriter, 500);
    }

    // Compteur d'animations pour les compétences
    const animateSkillTags = () => {
        const tags = document.querySelectorAll('.skill-tag');
        tags.forEach((tag, index) => {
            setTimeout(() => {
                tag.style.opacity = '0';
                tag.style.transform = 'scale(0.8)';
                tag.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    tag.style.opacity = '1';
                    tag.style.transform = 'scale(1)';
                }, 50);
            }, index * 30);
        });
    };

    // Lancer l'animation des tags après le chargement
    setTimeout(animateSkillTags, 1000);

    // Log pour le debug
    console.log('🚀 CV chargé avec succès!');
    console.log('💡 Astuce: Utilisez Ctrl+P ou Cmd+P pour imprimer le CV');
});

// Style pour l'animation rainbow (easter egg)
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    .fade-in-tag {
        animation: fadeInScale 0.5s ease forwards;
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);