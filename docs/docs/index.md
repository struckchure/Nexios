<!-- Hero Section -->
<div style="
    background: url('assets/nexios-hero-bg.jpg') center/cover no-repeat;" class="flex flex-col items-center">
    <img src="./nexiohero.png" alt="Nexios" class="w-full max-w-full">
    <h1 style="margin: 10px 0; font-size: 42px;">Nexios Framework</h1>
    <p style="font-size: 18px;">High-performance, easy to learn, and built for modern web applications.</p>
    <a href="/introduction"
   class="mt-5 inline-block bg-red-600 hover:bg-red-700 focus:ring-4 focus:ring-red-300 transition duration-300 px-4 py-2 rounded-lg text-white font-medium shadow-md">
    Get Started
</a>

</div>

## Why Choose Nexios?

<div class="flex flex-col md:flex-row w-full gap-2">
    <div class="border-[0.5px] border-purple-600 flex-1 text-center rounded-md p-4">
        <h3>🚀 High Performance</h3>
        <p>Optimized for speed and efficiency, handling thousands of requests per second.</p>
    </div>
    <div class="border-[0.5px] border-purple-600 flex-1 text-center rounded-md p-4">
        <h3>🛠️ Easy to Use</h3>
        <p>Minimal setup, clear syntax, and developer-friendly documentation.</p>
    </div>
    <div class="border-[0.5px] border-purple-600 flex-1 text-center rounded-md p-4">
        <h3>🌍 Scalable</h3>
        <p>Designed to grow with your application, from small projects to enterprise solutions.</p>
    </div>
</div>


## Nexios vs Other Frameworks

| Feature      | Nexios 🚀 | FastAPI ⚡ | Django 🏗 | Flask 🍶 |
|-------------|----------|----------|---------|--------|
| Speed       | ⚡⚡⚡⚡⚡  | ⚡⚡⚡⚡  | ⚡⚡  | ⚡⚡⚡  |
| Ease of Use | ✅✅✅✅✅ | ✅✅✅✅ | ✅✅✅ | ✅✅✅✅ |
| ORM Support | Any! | SQLAlchemy | Django ORM | SQLAlchemy |
| Async Support | ✅ | ✅ | ❌ (Django 4.1+ has partial) | ❌ |
| Authentication | ✅  | ✅ | ✅ | ❌ |
| Built-in Admin Panel | Coming Soon | ❌ | ✅ | ❌ |
| Best For | APIs & Full Apps | APIs | Full-stack Web Apps | Small Apps |

## Stay Connected

<div style="text-align: center; margin-top: 40px;">
    <a href="https://github.com/techwithdunamix/nexios" style="margin: 0 10px;">
        <img src="https://img.shields.io/badge/GitHub-Nexios-blue?logo=github" alt="GitHub">
    </a>
    <a href="https://medium.com/@techwithdunamix" style="margin: 0 10px;">
        <img src="https://img.shields.io/badge/Medium-TechWithDunamix-green?logo=medium" alt="Medium">
    </a>
</div>


##Create and activate a virtual environment, then install Nexios.
1. Create and Activate a Virtual Environment

Before installing Nexios, it's recommended to use a virtual environment to keep dependencies isolated.

### On Windows (CMD or PowerShell):
```sh
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux (Terminal):
```sh
python3 -m venv venv
source venv/bin/activate
```

2. Install Nexios

Once the virtual environment is active, install Nexios using pip:
```sh
pip install nexios-api
```

3. Verify Installation

Check if Nexios is installed correctly by running:
```sh
nexios
```
if nexios is installed the current version will be displayed
