$("#input").submit(function() {
	uri = $("select[name=uri]").val();
	$("#output").text('');
	$.post("/api/"+uri, $("#input").serialize(), function(data) {
		$("#output").text(data);
	}, 'text');
	return false;
});
$("#submit_button").mousedown(function() {
	$("#query").text('');
	$("#query").text($("#input").serialize();
});
