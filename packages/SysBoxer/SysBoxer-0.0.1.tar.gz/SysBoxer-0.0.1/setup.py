from setuptools import setup

setup(
    name='SysBoxer',
    version='0.0.1',
    packages=['SysBoxer'],
    url='https://github.com/roiterorh/sysboxer',
    install_requires=[
        'docker',
        'pyaml',
    ],
    download_url='https://github.com/roiterorh/sysboxer/archive/refs/tags/v0.0.1-alpha.tar.gz',
    author_email='nicolas.roitero@roihunter.com',
    author='Nicolas Roitero',

)


# setup(

#   license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
#   description = 'TYPE YOUR DESCRIPTION HERE',   # Give a short description about your library
#   author = 'YOUR NAME',                   # Type in your name


#   download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
#   keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best

#   classifiers=[
#     'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
#     'Intended Audience :: Developers',      # Define that your audience are developers
#     'Topic :: Software Development :: Build Tools',
#     'License :: OSI Approved :: MIT License',   # Again, pick a license
#     'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
#     'Programming Language :: Python :: 3.4',
#     'Programming Language :: Python :: 3.5',
#     'Programming Language :: Python :: 3.6',
#   ],
# )
