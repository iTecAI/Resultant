import { Component, Children, cloneElement, useState } from "react";
import Icon from "../icons";

function FieldWrapper(
    props = {
        fieldName: "",
        label: "",
        icon: "",
        children: [],
        fieldType: "",
        iconClass: null,
        valid: true,
        submessage: "",
    }
) {
    return (
        <div
            className={
                "field" +
                (props.fieldType ? " " + props.fieldType : "") +
                (props.icon ? " icon" : "") +
                (props.valid ? "" : " invalid") +
                (props.submessage ? " submessage" : "")
            }
            data-name={props.fieldName}
        >
            <div className="label noselect">
                {props.icon ? (
                    <Icon name={props.icon} category={props.iconClass} />
                ) : null}
                <span className="label-name">{props.label}</span>
            </div>
            <div className="field-input">
                <div className="submessage">{props.submessage}</div>
                {props.children}
            </div>
        </div>
    );
}

export default class Field extends Component {
    constructor(
        props = {
            values: {},
            onChange: () => {},
            onUpdate: () => {},
            fieldName: "newField",
            label: "Field",
            icon: null,
            iconClass: null,
            initialValue: null,
            validator: null,
        }
    ) {
        super(props);
        this.getInput = function (e) {
            this.setValue(e.target.value);
            return e.target.value;
        }.bind(this);
        this.handleChange = async function (e) {
            var value = this.getInput(e);
            this.setValue(value);
            var valid;
            if (this.props.validator) {
                valid = await this.props.validator(value, this.state, this);
            } else {
                valid = true;
            }
            if (valid === true) {
                this.setState({ valid: true, validMessage: "" });
                this.props.onChange(this.state.values);
            } else {
                this.setState({ valid: false, validMessage: valid });
            }
        }.bind(this);
        this.setValue = (value) => {
            var vals = this.state.values;
            vals[this.state.fieldName] = value;
            this.setState({ values: vals });
        };
        this.setValues = (values) => {
            var vals = this.state.values;
            for (var key of Object.keys(values)) {
                vals[key] = values[key];
            }
            this.setState({ values: vals });
        };
        this.state = {
            valid: true,
            validMessage: "",
            values: props.values,
            fieldName: props.fieldName,
            label: props.label,
            icon: props.icon,
            iconClass: props.iconClass,
        };
        this.state.values[this.state.fieldName] = this.props.initialValue || "";
        this.onUpdate = this.props.onUpdate || (() => {});
    }

    componentDidUpdate() {
        this.onUpdate(this.state);
    }

    render() {
        return (
            <FieldWrapper
                fieldName={this.state.fieldName}
                fieldType=""
                label={this.state.label}
                icon={this.state.icon}
                iconClass={this.state.iconClass}
                valid={this.state.valid}
                submessage={this.state.validMessage}
            >
                <input
                    onChange={this.handleChange}
                    value={this.state.values[this.state.fieldName]}
                    className="field-entry"
                />
            </FieldWrapper>
        );
    }
}

export class Input extends Field {
    constructor(props = { placeholder: null, type: null }) {
        super(props);
    }

    render() {
        return (
            <FieldWrapper
                fieldName={this.state.fieldName}
                fieldType="input"
                label={this.state.label}
                icon={this.state.icon}
                iconClass={this.state.iconClass}
                valid={this.state.valid}
                submessage={this.state.validMessage}
            >
                <input
                    onChange={this.handleChange}
                    value={this.state.values[this.state.fieldName]}
                    placeholder={this.props.placeholder}
                    type={this.props.type || "text"}
                    className="field-entry"
                />
            </FieldWrapper>
        );
    }
}

export class Select extends Field {
    componentDidUpdate() {
        if (
            this.props.children.length > 0 &&
            this.state.values[this.state.fieldName] === ""
        ) {
            for (var child of this.props.children) {
                if ((child || {}).props) {
                    this.setValue(child.props.value);
                    (this.props.validator || (() => {}))(
                        this.state.values[this.state.fieldName],
                        this.state,
                        this
                    );
                    break;
                }
            }
        }
        super.componentDidUpdate();
    }

    render() {
        return (
            <FieldWrapper
                fieldName={this.state.fieldName}
                fieldType="select"
                label={this.state.label}
                icon={this.state.icon}
                iconClass={this.state.iconClass}
                valid={this.state.valid}
                submessage={this.state.validMessage}
            >
                <select
                    onChange={this.handleChange}
                    value={this.state.values[this.state.fieldName]}
                    className="field-entry"
                >
                    {this.props.children}
                </select>
            </FieldWrapper>
        );
    }
}

export function HLine() {
    return <span className="form-element hline"></span>;
}

export class Range extends Field {
    constructor(props = { min: 0, max: 0, step: 1 }) {
        super(props);
        this.setValue(
            this.state.values[this.state.fieldName] === ""
                ? 0
                : this.state.values[this.state.fieldName]
        );

        this.getInput = function (e) {
            this.setValue(Number(e.target.value));
            return Number(e.target.value);
        }.bind(this);
    }

    componentDidUpdate() {
        setInterval(() => {
            if (this.state.values[this.state.fieldName] > this.props.max) {
                this.setValue(this.props.max);
            }
            if (this.state.values[this.state.fieldName] < this.props.min) {
                this.setValue(this.props.min);
            }
            if (isNaN(Number(this.state.values[this.state.fieldName]))) {
                this.setValue(this.props.min);
            }
        }, 0);
    }

    render() {
        return (
            <FieldWrapper
                fieldName={this.state.fieldName}
                fieldType="range"
                label={this.state.label}
                icon={this.state.icon}
                iconClass={this.state.iconClass}
                valid={this.state.valid}
                submessage={this.state.validMessage}
            >
                <input
                    onChange={this.handleChange}
                    value={this.state.values[this.state.fieldName]}
                    type="range"
                    className="field-entry"
                    min={this.props.min}
                    max={this.props.max}
                    step={this.props.step}
                />
                <div className="range-shroud">
                    <div className="range-inner">
                        <span
                            className="marker"
                            style={{
                                left:
                                    ((this.state.values[this.state.fieldName] -
                                        this.props.min) /
                                        (this.props.max - this.props.min)) *
                                        100 +
                                    "%",
                            }}
                        />
                        <span
                            className="fill"
                            style={{
                                width:
                                    "calc(" +
                                    ((this.state.values[this.state.fieldName] -
                                        this.props.min) /
                                        (this.props.max - this.props.min)) *
                                        100 +
                                    "% + 20px)",
                            }}
                        />
                    </div>
                </div>
                <input
                    onChange={this.handleChange}
                    value={this.state.values[this.state.fieldName] || 0}
                    type="text"
                    className="value-display"
                />
            </FieldWrapper>
        );
    }
}

export class Switch extends Field {
    constructor(props = { min: 0, max: 0, step: 1 }) {
        super(props);
        this.setValue(
            this.state.values[this.state.fieldName] === ""
                ? false
                : this.state.values[this.state.fieldName] === true
        );

        this.getInput = function (e) {
            this.setValue(e.target.checked);
            return e.target.checked;
        }.bind(this);
    }

    componentDidUpdate() {
        if (this.state.values[this.state.fieldName] === "") {
            this.setValue(this.props.initialValue || false);
        }
        super.componentDidUpdate();
    }

    render() {
        return (
            <FieldWrapper
                fieldName={this.state.fieldName}
                fieldType="switch"
                label={this.state.label}
                icon={this.state.icon}
                iconClass={this.state.iconClass}
                valid={this.state.valid}
                submessage={this.state.validMessage}
            >
                <input
                    onChange={this.handleChange}
                    checked={this.state.values[this.state.fieldName]}
                    type="checkbox"
                    className="field-entry"
                />
                <div className="check-shroud">
                    <span className="handle" />
                </div>
            </FieldWrapper>
        );
    }
}

export function Section(
    props = {
        children: [],
        title: "",
        icon: "",
        iconClass: "",
        values: {},
        onChange: () => {},
    }
) {
    const [expanded, setExpanded] = useState(false);
    return (
        <div className={"form-section" + (expanded ? " expanded" : "")}>
            <div className="title" onClick={() => setExpanded(!expanded)}>
                <Icon name={props.icon} category={props.iconClass} />
                <span className="title-text">{props.title}</span>
                <button className="expand">
                    <Icon name="chevron_down" />
                </button>
            </div>
            <div className="section-items">
                {Children.map(props.children, (child) => {
                    return cloneElement(child, {
                        values: props.values,
                        onChange: props.onChange,
                    });
                })}
            </div>
        </div>
    );
}
