#!/bin/bash
#Use on CentOS

if [ -s /etc/centos-release ]; 
	then 
		yum -y groupinstall "Development Tools"
		yum -y install openssl-devel readline-devel libxml2-devel libxslt-devel mysql mysql-devel mysql-libs mysql-server urw-fonts libXext-devel
		service mysqld start
		mysql_secure_installation
		chkconfig mysqld on
		cd /opt
		wget ftp://ftp.sunet.se/pub/multimedia/graphics/ImageMagick/ImageMagick-6.8.3-7.tar.gz
		wget http://pyyaml.org/download/libyaml/yaml-0.1.4.tar.gz
		#git clone git://github.com/jcsalterego/wkhtmltopdf-qt.git wkhtmltopdf-qt
		#wget http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.11.0_rc1.tar.bz2
		wget http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p392.tar.gz
		wget http://production.cf.rubygems.org/rubygems/rubygems-2.0.2.tgz
		wget -O snorby.zip https://github.com/Snorby/snorby/zipball/v2.5.6
		tar xzf ImageMagick-6.8.3-7.tar.gz
		tar xzf yaml-0.1.4.tar.gz
		tar xzf ruby-1.9.3-p392.tar.gz
		tar xzf rubygems-2.0.2.tgz
		#tar jxvf wkhtmltopdf-0.11.0_rc1.tar.bz2
		unzip snorby.zip
		cd ImageMagick-6.8.3-7
		./configure && make && make install
		cd ../yaml-0.1.4
		./configure && make && make install
		#cd ../wkhtmltopdf-qt
		#./configure -nomake tools,examples,demos,docs,translations -opensource -prefix ../wkqt && make && make install
		cd ../ruby-1.9.3-p392
		./configure && make && make install
		cd ../rubygems-2.0.2
		ruby setup.py
		cd ../Snorby-snorby-*
		gem install bundler
		sed -i s/"gem 'rake', '0.9.2'"/"gem 'rake', '> 0.9.2'"/g Gemfile
		sed -i s/"gem 'netaddr',                     '~> 1.5.0'"/"gem 'netaddr',                     '~> 1.5.0'\ngem 'orm_adapter'"/g Gemfile
		sed -i s/"rake (0.9.2)"/"rake (0.9.2.2)"/g Gemfile.lock
		
		echo "Now go configure config/snorby_config.yml and config/database.yml"
		echo "Just remove the example and edit it."
		echo "Then run: bundle install"
		echo "After that: snorby:setup"
		echo "You'll see see output, there will be around 9 lines of output"
		echo ""
		echo "After that is done run: iptables -I INPUT -p tcp --dport 3000 -m state --state=NEW,ESTABLISHED,RELATED -j ACCEPT"
		echo "Or any other port that you defined in snorby_config.yml"
		echo ""
		echo ""
		echo "Now run: rails server -e production    from inside the Snorby folder and you should be able to connect to the serve on the defined port"
		echo "Login: snorby@snorby.org   Pass: snorby"
	else 
		echo "I said on CentOS, not some other distro."; 
fi