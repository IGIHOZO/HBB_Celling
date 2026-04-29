def generate_csv(csv_data):
    """
    Generate CSV string from extracted data
    """
    if not csv_data:
        return "MSISDN,Custom1,Custom2,Custom8,BillingDay,Custom3\n"
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)  # Quote all fields to handle commas properly
    
    # Write header
    writer.writerow(['MSISDN', 'Custom1', 'Custom2', 'Custom8', 'BillingDay', 'Custom3'])
    
    # Write data rows
    for row in csv_data:
        writer.writerow([
            row.get('MSISDN', ''),
            row.get('Custom1', ''),
            row.get('Custom2', ''),
            row.get('Custom8', ''),
            row.get('BillingDay', ''),
            row.get('Custom3', '')
        ])
    
    return output.getvalue()
