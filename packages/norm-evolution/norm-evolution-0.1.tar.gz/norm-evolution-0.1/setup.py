from distutils.core import setup

setup(
  name = 'norm-evolution',         
  packages = ['norm_evolution'],   
  version = '0.1',      
  license='MIT',        
  description = 'Simulates which strategy evolves when agents immitate their neighbors',   
  author = 'ankurtutlani',                   
  author_email = 'ankur.tutlani@gmail.com',      
  url = 'https://github.com/ankur-tutlani/norm-evolution',   
  download_url = 'https://github.com/ankur-tutlani/norm-evolution/archive/refs/tags/v_01.tar.gz',    
  keywords = ['game theory', 'evolutionary game', 'social norms','multi-agents','evolution','circular network'],   
  install_requires=[            
          'numpy',
		  'pandas',
		  'random'
		  
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
												
	'Programming Language :: Python :: 3.7',
  ],
)