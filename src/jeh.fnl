(fn html [code]
		(.. "<html>" (.. code "</html>"))
	)

(html :hello)

{:html html}
