<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor
        xmlns="http://www.opengis.net/sld"
        xmlns:sld="http://www.opengis.net/sld"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:gml="http://www.opengis.net/gml"
        version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>{title}</sld:Name>
    <sld:UserStyle>
      <sld:Name>{table}</sld:Name>
      <sld:Title>{title}</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>{table}</sld:Name>
          <sld:Title>{title}</sld:Title>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#AAAAAA</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke/>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>

