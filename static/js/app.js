var payment = {}

payment.method = m.prop('euros');

payment.Method = function(data) {
    this.id = data.id;
    this.icon = data.icon;
    this.title = data.title;
    this.subtitle = data.subtitle;
};


payment.vm = (function() {
    var vm = {}
    vm.init = function() {
        vm.paymentMethod = m.prop('euros');
        vm.list = new Array;
        vm.list.push(
            new payment.Method({
                id: 'p-euros',
                icon: 'icon-euro',
                title: 'Euros',
                subtitle: 'Starting from 0€'
            }),
            new payment.Method({
                id: 'p-flattr',
                icon: 'icon-flattr',
                title: 'Flattr',
                subtitle: 'Flattr my page'
            })
        );
    }
    return vm
}())


//the controller defines what part of the model is relevant for the current page
//in our case, there's only one view-model that handles everything
payment.controller = function() {
    payment.vm.init()
}

//here's the vietodow
payment.view = function() {
    return m("span", payment.vm.paymentMethod());
};

//initialize the application
m.mount(document.getElementById('paymentMethod'), {controller: payment.controller, view: payment.view});
