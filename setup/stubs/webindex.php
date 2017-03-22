<?php
	$parameters	= "";

	// collect all GET and POST parameters provided by the user
	$keys		= array_keys($_GET);
	foreach($keys as $key)
		$parameters .= trim($key) . "=" . trim($_GET[$key]) . " ";

	$keys		= array_keys($_POST);
	foreach($keys as $key)
		$parameters .= trim($key) . "=" . trim($_POST[$key]) . " ";

	// create a reference to the script
	// the {installationdir} string will be replaced by the directory 
	// where the main WebIndex executable is located
	$webindex	= "{installationdir}/webindex.sh";

	// fetch any 'header' output from the script
	$pipe		= popen("$webindex header $parameters", "r");
	$header		= "";
	while (!feof($pipe))
		$header .= fgets($pipe, 1024);
	pclose($pipe);

	// write header to the browser
	header($header);

	$output	= $_GET['output'];

	// set a special 'caller' variable (needed for OAI and HTML output)
	$caller	= "caller=http://" . $_SERVER['HTTP_HOST'] . $PHP_SELF . "?output=" . $output;

	// display output from script
	passthru("$webindex display $output $parameters $caller");
?>
