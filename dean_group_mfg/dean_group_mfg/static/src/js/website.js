/* global odoo */
odoo.define('dean_group_mfg.website', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // ── Scroll reveal ─────────────────────────────────
    publicWidget.registry.DGReveal = publicWidget.Widget.extend({
        selector: 'body.website',
        start: function () {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) {
                        e.target.classList.add('dg-in');
                    }
                });
            }, { threshold: 0.08 });

            document.querySelectorAll('.dg-reveal').forEach(function (el) {
                observer.observe(el);
            });

            // Nav scroll effect
            window.addEventListener('scroll', function () {
                var nav = document.querySelector('.navbar');
                if (nav) {
                    nav.style.boxShadow = window.scrollY > 40
                        ? '0 4px 32px rgba(0,0,0,.6)'
                        : 'none';
                }
            });

            return this._super.apply(this, arguments);
        },
    });

    return publicWidget.registry.DGReveal;
});
