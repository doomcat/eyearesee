$("#input").submit(function() {
	uri = $("select[name=uri]").val();
	$("#output").text('');
	data = $("#input").serialize();
	$.post("/api/"+uri, clean_data(data),
		function(data) {
			$("#output").text(data);
		},
	'text');
	return false;
});

function clean_data(data) {
	return data.replace(/[^&]+=\.?(?:&|$)/g, '');
}

$("#submit_button").mousedown(function() {
	$("#query").text('');
	$("#query").text(clean_data($("#input").serialize()));
});
