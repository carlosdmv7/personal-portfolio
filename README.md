# Carlos De Manuel - Portfolio

Personal portfolio website showcasing my experience as a Data Analyst and Data Scientist.

## 🚀 Live Demo

Visit the live site at: `https://yourusername.github.io/portfolio`

## 📁 Project Structure

```
portfolio/
│
├── index.html          # Main HTML structure
├── styles.css          # All styling and animations
├── config.js           # ⭐ YOUR PERSONAL DATA (edit this!)
├── app.js              # JavaScript logic (no need to edit)
└── README.md           # Documentation
```

## 🚀 Quick Start - Edit Your Info

### Step 1: Update `config.js`

Open `config.js` and update your personal information:

```javascript
const CONFIG = {
    contact: {
        email: "carlos@example.com",           // ← Change this
        phone: "+34 123 456 789",              // ← Change this
        linkedin: "https://linkedin.com/in/carlos-demanuel",  // ← Change this
        github: "https://github.com/carlosdemanuel",          // ← Change this
    },
    
    personal: {
        name: "Carlos De Manuel",
        shortName: "Carlos",
        availableForWork: true,  // Set to false if not available
    },
    
    // ... and so on
};
```

**Everything you need to update is in this one file!** The rest updates automatically.

### Step 2: Upload to GitHub

1. Create repository named `portfolio` or `yourusername.github.io`
2. Upload ALL files: `index.html`, `styles.css`, `config.js`, `app.js`, `README.md`
3. Go to Settings → Pages → Enable GitHub Pages
4. Done! 🎉

## ✏️ How to Update Your Portfolio

### Add New Projects

Open `config.js` and add to the `projects` array:

```javascript
projects: [
    // ... existing projects
    {
        title: "My New Project",
        description: "Description of what this project does...",
        technologies: ["Python", "React", "PostgreSQL"],
        links: {
            github: "https://github.com/yourname/project",
            demo: "https://project-demo.com"
        },
        image: "images/new-project.jpg" // Optional
    }
]
```

### Add New Certifications

Add to the `certifications` array in `config.js`:

```javascript
certifications: [
    // ... existing certs
    {
        name: "AWS Solutions Architect",
        issuer: "Amazon Web Services",
        date: "Jan 2025",
        technologies: ["AWS", "Cloud", "Architecture"],
        credentialId: "ABC123",
        credentialUrl: "https://credential-link.com"
    }
]
```

### Update Skills

Modify the `skills` object in `config.js`:

```javascript
skills: {
    "Languages & Databases": {
        icon: "💻",
        items: ["Python", "SQL", "JavaScript"] // Add or remove skills
    },
    // ... other categories
}
```

### Update Work Experience

Add new positions to `experience` array:

```javascript
experience: [
    {
        title: "Senior Data Analyst",
        company: "New Company",
        type: "Full-time",
        location: "Madrid, Spain",
        locationType: "Remote",
        period: "Jan 2026 - Present",
        current: true,
        description: "What you do here...",
        technologies: ["Python", "Snowflake", "Power BI"]
    },
    // ... previous experience
]
```

### Change Theme Colors

Edit CSS variables in `styles.css`:

```css
:root {
    --accent: #3b82f6;  /* Change to your color */
    --gradient-1: #3b82f6;
    --gradient-2: #8b5cf6;
}
```

## 🎨 Customization

### Update Contact Information (Most Important!)

1. Open `config.js`
2. Find the `contact` section:
```javascript
contact: {
    email: "your.email@example.com",      // ← Update
    phone: "+34 123 456 789",             // ← Update
    linkedin: "https://linkedin.com/in/your-profile",  // ← Update
    github: "https://github.com/your-username",        // ← Update
}
```
3. Save the file
4. Push to GitHub - **done!**

All contact buttons, footer links, and email addresses will update automatically across the entire site.

### Add Images

1. Create an `images/` folder in your repository
2. Add your profile photo as `profile.jpg`
3. Add project screenshots
4. Update `index.html` to include images:

```html
<img src="images/profile.jpg" alt="Carlos De Manuel" class="profile-image">
```

## 📝 Adding New Sections

To add a new section (e.g., "Skills", "Publications"):

1. Add navigation link in `<nav>`:
```html
<li><a href="#skills">Skills</a></li>
```

2. Add section in `<main>`:
```html
<section id="skills" class="skills">
    <div class="container">
        <h2 class="section-title">Skills</h2>
        <!-- Your content here -->
    </div>
</section>
```

3. Add styling in `styles.css` if needed

## 🔄 Keeping It Updated

### Regular Updates
- Add new projects as you complete them
- Update experience section with new positions
- Add new certifications
- Keep tech stacks current

### Version Control
```bash
# Make changes to files
git add .
git commit -m "Add new project: Data Pipeline"
git push
```

GitHub Pages will automatically rebuild and deploy your changes.

## 📱 Mobile Responsive

The portfolio is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## 🚀 Advanced Features (Optional)

### Add Smooth Scrolling

Add to `index.html` before `</body>`:

```html
<script>
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
</script>
```

### Add Analytics

Add Google Analytics or similar before `</head>` in `index.html`

### Add Contact Form

Integrate with Formspree, Netlify Forms, or similar service

## 📄 License

Feel free to fork and modify this portfolio for your own use!

## 🤝 Contributing

This is a personal portfolio, but suggestions are welcome via issues.

## 📧 Contact

- LinkedIn: [Your LinkedIn]
- GitHub: [Your GitHub]
- Email: your.email@example.com

---

Built with ❤️ by Carlos De Manuel