from distutils.core import setup

setup(
  name = 'yungestgram',         
  packages = ['yungestgram'],   
  version = '25.6.22.2',      
  license='MIT',        
  description = 'Telegram bot library',   
  author = 'yungestDev',                   
  author_email = 'yungestmonsterhahaha@gmail.com',      
  #url = 'https://github.com/yungestdev/yungestWeb',   
  #download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    
  keywords = ['Telegram', 'Bot'],   
  install_requires=[            
        'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # 3 - Alpha 2 - Beta 1 - Stable/Final
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',      

  ],
)