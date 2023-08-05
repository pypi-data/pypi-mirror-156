window.kaggleOnActiveCellChangeEvt = function () {
    let kernel;

    if (typeof jupyterlab !== 'undefined' && jupyterlab.shell.currentWidget?.context?.sessionContext.session?.kernel) {
        kernel = jupyterlab.shell.currentWidget?.context?.sessionContext.session?.kernel;
    }

    const onActiveCellChanged = (event) => {
        if (event.activeCell) {
            if (kernel) {
                kernel.requestExecute({
                    code: `cfpy_active_cell_id = '${event.activeCell.model.id}'`,
                    silent: true
                });
            }
        }
    }

    if (kernel) {
        jupyterlab.shell.currentWidget.content.activeCellChanged.connect(onActiveCellChanged, this);
    }    
};

(() => {
    window.kaggleOnActiveCellChangeEvt();
})();
