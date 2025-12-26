# Carlos De Manuel - Portfolio

Personal portfolio website showcasing my experience as a Data Analyst and Data Scientist.

## 🚀 Live Demo

Visit the live site at: `https://yourusername.github.io/portfolio`

## 📁 Project Structure

```
portfolio/
│
├── index.html          # Main HTML file
├── styles.css          # Styling
├── projects.json       # Project data (easy to update)
└── README.md          # This file
```

## 🛠️ Setup Instructions

### 1. Create GitHub Repository

1. Go to GitHub and create a new repository
2. Name it: `portfolio` (or `yourusername.github.io` for direct hosting)
3. Make it public
4. Don't initialize with README (we'll upload files)

### 2. Upload Files

**Option A: Using GitHub Web Interface**
1. Click "uploading an existing file"
2. Drag and drop `index.html`, `styles.css`, and `README.md`
3. Commit changes

**Option B: Using Git Command Line**
```bash
git init
git add .
git commit -m "Initial portfolio commit"
git branch -M main
git remote add origin https://github.com/yourusername/portfolio.git
git push -u origin main
```

### 3. Enable GitHub Pages

1. Go to repository Settings
2. Navigate to "Pages" in the left sidebar
3. Under "Source", select "main" branch
4. Click Save
5. Your site will be live at `https://yourusername.github.io/portfolio`

## ✏️ How to Add Projects

### Method 1: Direct HTML Edit (Simple)

Edit `index.html` and find the `<section id="projects">` section. Add a new project card:

```html
<div class="project-card">
    <h3>Project Name</h3>
    <p>Project description goes here. Explain what the project does and its impact.</p>
    <div class="tech-stack">
        <span class="tech-tag">Python</span>
        <span class="tech-tag">SQL</span>
        <span class="tech-tag">Power BI</span>
    </div>
    <div class="project-links">
        <a href="https://github.com/yourusername/project" class="project-link">View Project →</a>
    </div>
</div>
```

### Method 2: Using projects.json (Advanced - Optional)

Create a `projects.json` file to manage projects separately:

```json
{
  "projects": [
    {
      "title": "Trustworthy AI Framework",
      "description": "Open-source framework for building explainable and fair AI models in healthcare.",
      "technologies": ["Python", "SHAP", "Scikit-learn"],
      "link": "https://github.com/yourusername/trustworthy-ai",
      "image": "images/project1.png"
    },
    {
      "title": "KPI Dashboard System",
      "description": "Enterprise-wide KPI management application built with Streamlit.",
      "technologies": ["Python", "Streamlit", "Snowflake", "Power BI"],
      "link": "https://github.com/yourusername/kpi-dashboard",
      "image": "images/project2.png"
    }
  ]
}
```

Then add JavaScript to `index.html` to load projects dynamically (see Advanced Setup below).

## 🎨 Customization

### Update Personal Information

1. **Contact Links**: Edit the contact section in `index.html`
   - Update LinkedIn URL
   - Update GitHub URL
   - Update email address

2. **Hero Section**: Modify your name and description in the hero section

3. **Colors**: Change colors in `styles.css` by modifying the `:root` variables:
```css
:root {
    --accent: #3b82f6;  /* Change to your preferred color */
}
```

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