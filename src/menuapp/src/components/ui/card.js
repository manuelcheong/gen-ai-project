const Card = ({ className, children, ...props }) => {
    return (
      <div
        className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
        {...props}
      >
        {children}
      </div>
    )
  }
  
  const CardHeader = ({ className, ...props }) => {
    return (
      <div
        className={`flex flex-col space-y-1.5 p-6 ${className}`}
        {...props}
      />
    )
  }
  
  const CardTitle = ({ className, children, ...props }) => {
    if (!children) {
      return null; // Or handle empty state appropriately
    }
    return (
      <h3
        className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
        {...props}
      />
    )
  }
  
  const CardDescription = ({ className, ...props }) => {
    return (
      <p
        className={`text-sm text-muted-foreground ${className}`}
        {...props}
      />
    )
  }
  
  const CardContent = ({ className, ...props }) => {
    return (
      <div
        className={`p-6 pt-0 ${className}`}
        {...props}
      />
    )
  }
  
  const CardFooter = ({ className, ...props }) => {
    return (
      <div
        className={`flex items-center p-6 pt-0 ${className}`}
        {...props}
      />
    )
  }
  
  export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter }
  