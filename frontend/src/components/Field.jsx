export default function Field({ label, error, ...props }) { return <label className="field"><span>{label}</span><input {...props} />{error && <small className="field-error">{error}</small>}</label> }
