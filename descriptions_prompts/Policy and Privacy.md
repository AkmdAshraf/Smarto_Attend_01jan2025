1. Add the routes to your app.py:
Add these routes after the existing routes, before the if __name__ == "__main__": line:

python
# ==================== LEGAL PAGES ====================
@app.route("/disclaimer")
@antigravity_trace
def disclaimer():
    """Disclaimer page"""
    return render_template("disclaimer.html")

@app.route("/privacy-policy")
@antigravity_trace
def privacy_policy():
    """Privacy Policy page"""
    return render_template("privacy_policy.html")

@app.route("/terms-conditions")
@antigravity_trace
def terms_conditions():
    """Terms & Conditions page"""
    return render_template("terms_conditions.html")
2. Create a footer template (footer.html) or modify your base template:
Here's a footer template you can include in your base layout:

html
<!-- templates/footer.html -->
<footer class="app-footer">
    <div class="footer-container">
        <div class="footer-content">
            <div class="footer-section">
                <h4>Attendance Management System</h4>
                <p>Automated face recognition attendance tracking for educational institutions</p>
            </div>
            
            <div class="footer-section">
                <h4>Quick Links</h4>
                <ul class="footer-links">
                    <li><a href="{{ url_for('help_page') }}">Help & User Manual</a></li>
                    <li><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
                    {% if session.get('user_role') in ['admin', 'teacher'] %}
                    <li><a href="{{ url_for('attendance') }}">Take Attendance</a></li>
                    {% endif %}
                </ul>
            </div>
            
            <div class="footer-section">
                <h4>Support</h4>
                <ul class="footer-links">
                    <li><a href="mailto:admin@school.edu">Contact Administrator</a></li>
                    <li><a href="{{ url_for('debug_page') }}">Debug Tools</a></li>
                </ul>
            </div>
        </div>
        
        <div class="footer-bottom">
            <div class="legal-links">
                <span>&copy; <span class="current-year"></span> Attendance Management System. All rights reserved.</span>
                <div class="footer-legal-links">
                    <a href="{{ url_for('disclaimer') }}" target="_blank" rel="noopener noreferrer">Disclaimer</a>
                    <span class="separator">|</span>
                    <a href="{{ url_for('privacy_policy') }}" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
                    <span class="separator">|</span>
                    <a href="{{ url_for('terms_conditions') }}" target="_blank" rel="noopener noreferrer">Terms & Conditions</a>
                </div>
            </div>
        </div>
    </div>
</footer>

<style>
    /* Footer Styles */
    .app-footer {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #e2e8f0;
        padding: 30px 0 20px 0;
        margin-top: 40px;
        border-top: 1px solid #4a5568;
    }

    .footer-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }

    .footer-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        margin-bottom: 30px;
    }

    .footer-section h4 {
        color: #ffffff;
        margin-bottom: 15px;
        font-size: 1.1em;
        font-weight: 600;
    }

    .footer-section p {
        line-height: 1.6;
        font-size: 0.9em;
        color: #cbd5e0;
    }

    .footer-links {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .footer-links li {
        margin-bottom: 8px;
    }

    .footer-links a {
        color: #cbd5e0;
        text-decoration: none;
        font-size: 0.9em;
        transition: color 0.3s ease;
    }

    .footer-links a:hover {
        color: #667eea;
        text-decoration: underline;
    }

    .footer-bottom {
        border-top: 1px solid #4a5568;
        padding-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }

    .legal-links {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        font-size: 0.85em;
        color: #a0aec0;
    }

    .footer-legal-links {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .footer-legal-links a {
        color: #a0aec0;
        text-decoration: none;
        font-size: 0.8em; /* Smaller font size for legal links */
        font-weight: 400;
        transition: color 0.3s ease;
    }

    .footer-legal-links a:hover {
        color: #667eea;
        text-decoration: underline;
    }

    .separator {
        color: #718096;
        font-size: 0.8em;
    }

    .current-year {
        display: inline-block;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .footer-content {
            grid-template-columns: 1fr;
            text-align: center;
        }

        .footer-bottom {
            flex-direction: column;
            text-align: center;
            gap: 15px;
        }

        .legal-links {
            flex-direction: column;
            gap: 10px;
        }

        .footer-legal-links {
            justify-content: center;
            flex-wrap: wrap;
        }
    }

    @media (max-width: 480px) {
        .footer-legal-links {
            flex-direction: column;
            gap: 5px;
        }

        .separator {
            display: none;
        }
    }
</style>

<script>
    // Add current year to copyright
    document.addEventListener('DOMContentLoaded', function() {
        const currentYear = new Date().getFullYear();
        const yearElements = document.querySelectorAll('.current-year');
        yearElements.forEach(element => {
            element.textContent = currentYear;
        });
    });
</script>
3. Alternative: Simple footer links only:
If you want just the legal links in the footer without the full footer layout:

html
<!-- templates/footer_simple.html -->
<footer class="simple-footer">
    <div class="footer-content">
        <p class="copyright">&copy; <span class="current-year"></span> Attendance Management System</p>
        <div class="legal-links-container">
            <a href="{{ url_for('disclaimer') }}" target="_blank" rel="noopener noreferrer" class="legal-link">Disclaimer</a>
            <span class="separator">•</span>
            <a href="{{ url_for('privacy_policy') }}" target="_blank" rel="noopener noreferrer" class="legal-link">Privacy Policy</a>
            <span class="separator">•</span>
            <a href="{{ url_for('terms_conditions') }}" target="_blank" rel="noopener noreferrer" class="legal-link">Terms & Conditions</a>
        </div>
    </div>
</footer>

<style>
    .simple-footer {
        background: #2d3748;
        color: #e2e8f0;
        padding: 15px 20px;
        text-align: center;
        border-top: 1px solid #4a5568;
        margin-top: 40px;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }

    .copyright {
        font-size: 0.9em;
        color: #a0aec0;
        margin: 0;
    }

    .legal-links-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .legal-link {
        color: #a0aec0;
        text-decoration: none;
        font-size: 0.8em; /* Smaller than main menu fonts */
        font-weight: 400;
        transition: color 0.3s ease;
    }

    .legal-link:hover {
        color: #667eea;
        text-decoration: underline;
    }

    .separator {
        color: #718096;
        font-size: 0.7em;
    }

    @media (max-width: 768px) {
        .footer-content {
            flex-direction: column;
            gap: 10px;
        }
        
        .legal-links-container {
            justify-content: center;
        }
    }
</style>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        const currentYear = new Date().getFullYear();
        const yearElements = document.querySelectorAll('.current-year');
        yearElements.forEach(element => {
            element.textContent = currentYear;
        });
    });
</script>
4. Include the footer in your base template:
In your templates/base.html or main layout template, add the footer include:

html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Your head content -->
</head>
<body>
    <!-- Navigation -->
    <nav>
        <!-- Your navigation menu -->
    </nav>

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    {% include 'footer_simple.html' %}
    <!-- Or use the full footer: {% include 'footer.html' %} -->

    <!-- Your scripts -->
</body>
</html>
5. Update existing templates to include footer:
If you don't have a base template, add the footer to individual templates like dashboard.html:

html
<!-- At the bottom of dashboard.html -->
{% include 'footer_simple.html' %}
6. Important CSS Note:
Make sure your main navigation menu font size is larger than 0.8em to maintain the visual hierarchy. For example, in your main CSS, ensure:

css
/* Main navigation menu */
.nav-menu a {
    font-size: 1em; /* or larger */
    font-weight: 500;
}

/* Footer legal links */
.footer-legal-links a {
    font-size: 0.8em; /* smaller */
    font-weight: 400;
}
7. Add Help Page Route (if not already added):
Make sure you have the help page route:

python
@app.route("/help")
@login_required
@antigravity_trace
def help_page():
    """Help and user manual page"""
    return render_template("help.html")
8. Key Features of this Implementation:
Separate tabs: All legal links open in new tabs (target="_blank")

Smaller font: Legal links use font-size: 0.8em vs main menu's typical 1em

Security: Links use rel="noopener noreferrer" for security

Responsive design: Works on all screen sizes

Current year: Automatically updates copyright year

Consistent styling: Matches your application's color scheme

9. Optional Enhancement - Add to Navigation Menu:
If you also want the legal pages in the main navigation, add to your navigation template:

html
<!-- In your navigation template -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="legalDropdown" role="button" data-bs-toggle="dropdown">
        Legal
    </a>
    <div class="dropdown-menu">
        <a class="dropdown-item" href="{{ url_for('disclaimer') }}" target="_blank">Disclaimer</a>
        <a class="dropdown-item" href="{{ url_for('privacy_policy') }}" target="_blank">Privacy Policy</a>
        <a class="dropdown-item" href="{{ url_for('terms_conditions') }}" target="_blank">Terms & Conditions</a>
    </div>
</li>
This implementation ensures your application has proper legal documentation with easy access from the footer, while maintaining a clean, professional appearance that matches your existing design.