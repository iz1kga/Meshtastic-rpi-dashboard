import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "iMesh-Dashboard",
    version = "0.0.7",
    author = "iz1kga",
    author_email = "iz1kga@gmail.com",
    description = "Create Dashboard for serial connected meshtastic device",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/iz1kga/Meshtastic-rpi-dashboard",
    license = "apache 2.0",
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    packages = ["iMeshDashboard"],
    data_files=[('iMeshDashboard/conf', ['iMeshDashboard/conf/app.conf']),
                ('iMeshDashboard/templates', ['iMeshDashboard/templates/index.html', 'iMeshDashboard/templates/public.html', 'iMeshDashboard/templates/map.html']),
                ('iMeshDashboard/css', ['iMeshDashboard/css/bootstrap.min.css']),
                ('iMeshDashboard/js', ['iMeshDashboard/js/bootstrap.bundle.min.js', 'iMeshDashboard/js/jquery-3.5.1.min.js']),
    ],
    install_requires=["configparser>=5.0.1", "Flask==1.1.2", "Flask-BasicAuth==0.2.0", "meshtastic>=1.1.49",
                      "paho-mqtt==1.5.1", "timeago>=1.0.15", "waitress==1.4.4"],
    python_requires = '>=3.6',
    entry_points={
        "console_scripts": [
            "iMeshDashboard=iMeshDashboard:main",
        ]
    }
)
